from sklearn.model_selection import RandomizedSearchCV
from trainer.model import model_entrainer
from sklearn.ensemble import VotingClassifier
from skopt import BayesSearchCV
from skopt.space import Integer, Real, Categorical
from sklearn.metrics import confusion_matrix
import numpy as np
from tuple import Data_set, type_enum
"""
    Entraene un modrle RandomForest avec recherche d'hyperparamètres en 3 étapes:
    1. RandomizedSearch sur n_estimators, max_features, max_depth
    2. RandomizedSearch sur min_samples_leaf, min_samples_split
    3. Bayesian Optimization pour trouver les 5 meilleurs
    4. Vote avec les 5 meilleurs modeles
    
    Args:
        model: Le modele RandomForest a entraîner
        dataset: Le dataset contenant X_train, Y_train, X_dev, Y_dev
        
    Returns:
        trained_model: Objet model_entrainer avec le voting classifier
"""

def rf_trainer(model, dataset):

    # RECONNAITRE LE TYPE DU PROBLEME ET L'EQUILIBRE POUR DETERMINER LES METRIQUES
    # equilibre_labels=True signifie dataset équilibré, False signifie déséquilibré
    if dataset.equilibre_labels:
        # Dataset équilibré
        if dataset.type_probleme in [type_enum.MULTILABEL, type_enum.MULTICLASS]:
            scoring = 'f1_macro'
        else:  # BINARY_CLASSIFICATION
            scoring = 'accuracy'
    else:
        # Dataset déséquilibré : utiliser f1_weighted pour tenir compte du déséquilibre
        if dataset.type_probleme in [type_enum.MULTILABEL, type_enum.MULTICLASS]:
            scoring = 'f1_weighted'
        else:  # BINARY_CLASSIFICATION
            scoring = 'f1'

    # Préparer les données et adapter le format de Y selon le type de problème
    X_train = np.array(dataset.X_train)
    Y_train_raw = np.array(dataset.Y_train)
    X_dev = np.array(dataset.X_dev)
    Y_dev_raw = np.array(dataset.Y_dev)
    
    # Adapter le format de Y selon le type de problème
    if dataset.type_probleme == type_enum.MULTICLASS:
        # Pour multiclass : si one-hot encoding, convertir en indices
        if Y_train_raw.ndim == 2 and Y_train_raw.shape[1] > 1:
            Y_train = np.argmax(Y_train_raw, axis=1)
            Y_dev = np.argmax(Y_dev_raw, axis=1)
        elif Y_train_raw.ndim == 2 and Y_train_raw.shape[1] == 1:
            Y_train = Y_train_raw.ravel()
            Y_dev = Y_dev_raw.ravel()
        else:
            Y_train = Y_train_raw
            Y_dev = Y_dev_raw
    else:
        # Pour classification binaire
        if Y_train_raw.ndim == 2 and Y_train_raw.shape[1] == 1:
            Y_train = Y_train_raw.ravel()
            Y_dev = Y_dev_raw.ravel()
        else:
            Y_train = Y_train_raw
            Y_dev = Y_dev_raw

    # ETAPE 1: RandomizedSearch sur n_estimators, max_features, max_depth 
    param_dist_1 = {
        'n_estimators': [50, 100, 150, 200, 250, 300],
        'max_features': ['sqrt', 'log2', None],
        'max_depth': [10, 20, 30, 40, 50, None]
    }
    
    random_search_1 = RandomizedSearchCV(
        model, 
        param_distributions=param_dist_1,
        n_iter=20,
        cv=5,
        scoring= scoring,
        random_state=42,
        n_jobs=-1
    )
    random_search_1.fit(X_train, Y_train)
    
    best_params_step1 = random_search_1.best_params_

    # ETAPE 2: RandomizedSearch sur min_samples_leaf, min_samples_split 
    param_dist_2 = {
        # JE FIXE LES TROIS PREMIERS PARAM TROUVE
        'n_estimators': [best_params_step1['n_estimators']],
        'max_features': [best_params_step1['max_features']],
        'max_depth': [best_params_step1['max_depth']],
        'min_samples_leaf': [1, 2, 4, 6, 8, 10],
        'min_samples_split': [2, 5, 10, 15, 20]
    }
    
    random_search_2 = RandomizedSearchCV(
        model,
        param_distributions=param_dist_2,
        n_iter=15,
        cv=5,
        scoring= scoring,
        random_state=42,
        n_jobs=-1
    )
    random_search_2.fit(X_train, Y_train)

    #ON RECUPERE LES PARAMS
    best_params_step2 = random_search_2.best_params_

    # ETAPE 3: Bayesian Optimization pour top 3
    search_spaces = {
        'n_estimators': Integer(
            max(50, best_params_step2['n_estimators'] - 50),
            best_params_step2['n_estimators'] + 50
        ),
        'max_features': Categorical(['sqrt', 'log2', None]),
        'max_depth': Integer(10, 60) if best_params_step2['max_depth'] is not None else Categorical([None]),
        'min_samples_leaf': Integer(1, 15),
        'min_samples_split': Integer(2, 25)
    }
    
    bayes_search = BayesSearchCV(
        model,
        search_spaces=search_spaces,
        n_iter=30,
        cv=5,
        scoring=scoring,
        random_state=42,
        n_jobs=-1
    )
    bayes_search.fit(X_train, Y_train)

    # Recuperer les 3 meilleurs hyperparamètres
    results = bayes_search.cv_results_
    top_3_indices = np.argsort(results['mean_test_score'])[-3:][::-1]
    top_3_params = [results['params'][i] for i in top_3_indices]


    # Entrainer les cinq meilleurs models
    from concurrent.futures import ThreadPoolExecutor

    def train_single_model(params, model_class, X_train, Y_train, model_id):
        m = model_class(**params)
        m.fit(X_train, Y_train)
        return (f'model_{model_id}', m)
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(train_single_model, params, model.__class__, X_train, Y_train, i+1)
            for i, params in enumerate(top_3_params)
        ]
        top_3_models = [future.result() for future in futures]
    
    voting_model = VotingClassifier(
        estimators=top_3_models,
        voting='soft'
    )

    voting_model.fit(X_train, Y_train)

     # Creer l'objet de retour 
    trained_model = model_entrainer()
    trained_model.model_fiter = voting_model
    trained_model.hyperparameters = {
        'top_3_params': top_3_params,
        'best_from_bayes': bayes_search.best_params_
    }
    
    # Predictions et matrice de confusion
    predictions = voting_model.predict(X_dev)
    trained_model.confusion_matrix = confusion_matrix(Y_dev, predictions)
    
    return trained_model