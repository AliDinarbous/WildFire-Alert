
from sklearn.model_selection import RandomizedSearchCV
from automl.trainer.model import model_entrainer
from sklearn.ensemble import VotingClassifier
from skopt import BayesSearchCV
from skopt.space import Integer, Real, Categorical
from sklearn.metrics import confusion_matrix
import numpy as np
from automl.tuple import Data_set, type_enum
from concurrent.futures import ThreadPoolExecutor
from sklearn.metrics import classification_report

def gbc_trainer(model, dataset):
    """
    Entraine un GradientBoostClassifier avec recherche d'hyperparamètres en 3 étapes :
    1. randomizedSearch learning_rate + n_estimators
    2. randomizedSearch max_depth + max_depth + subsample + min_samples_split + min_samples_leaf 
    3. bayesianSearch sur les 7 hyperparam (re-tunnig) 
    4. Vote avec les 5 meilleurs modeles
    """

    # determiner le scoring selon le type de problème et l'equilibre
    # equilibre_labels=True signifie dataset équilibré, False signifie déséquilibré
    if dataset.equilibre_labels:
        # Dataset équilibré
        if dataset.type_probleme in [type_enum.MULTILABEL, type_enum.MULTICLASS]:
            scoring = 'f1_macro'
        else:  # BINARY_CLASSIFICATION
            scoring = 'accuracy'
    else:
        # Dataset déséquilibré : utiliser f1_weighted
        if dataset.type_probleme in [type_enum.MULTILABEL, type_enum.MULTICLASS]:
            scoring = 'f1_weighted'
        else:
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

    # ETAPE 1
    param_dist_1 = {
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'n_estimators': [50, 100, 150, 200, 250],
    }
    
    random_search_1 = RandomizedSearchCV(
        model,
        param_distributions=param_dist_1,
        n_iter=10,
        cv=5,
        scoring=scoring,
        random_state=42,
        n_jobs=-1
    )
    random_search_1.fit(X_train, Y_train)
    best_params_1 = random_search_1.best_params_

    # ETAPE 2 
    param_dist_2 = {
        'learning_rate': [best_params_1['learning_rate']],
        'n_estimators': [best_params_1['n_estimators']],
        'max_depth': [3, 5, 7, 9, 12],
        'subsample': [0.6, 0.7, 0.8, 0.9, 1.0],            
        'min_samples_split': [2, 4, 6, 8, 10],              
        'min_samples_leaf': [1, 2, 4, 6, 8, 10],  
    }

    random_search_2 = RandomizedSearchCV(
        model,
        param_distributions=param_dist_2,
        n_iter=10,
        cv=5,
        scoring=scoring,
        random_state=42,
        n_jobs=-1
    )
    random_search_2.fit(X_train, Y_train)
    best_params_2 = random_search_2.best_params_

    # ETAPE 3 
    search_spaces = {
    'learning_rate': Real(
        max(0.001, best_params_2['learning_rate'] - 0.05),
        min(0.3, best_params_2['learning_rate'] + 0.05)
    ),
    'n_estimators': Integer(
        max(50, best_params_2['n_estimators'] - 50),
        best_params_2['n_estimators'] + 50
    ),
    'max_depth': Integer(
        max(3, best_params_2['max_depth'] - 3),
        best_params_2['max_depth'] + 3
    ),
    'subsample': Real(
        max(0.5, best_params_2['subsample'] - 0.15),
        min(1.0, best_params_2['subsample'] + 0.15)
    ),
    'min_samples_split': Integer(
        max(2, best_params_2['min_samples_split'] - 3),
        best_params_2['min_samples_split'] + 3
    ),
    'min_samples_leaf': Integer(
        max(1, best_params_2['min_samples_leaf'] - 3),
        best_params_2['min_samples_leaf'] + 3
    ),  
    }

    bayes_search = BayesSearchCV(
        model,
        search_spaces=search_spaces,
        n_iter=20,
        cv=5,
        scoring=scoring,
        random_state=42,
        n_jobs=-1
    )
    bayes_search.fit(X_train, Y_train)

    # Top 5 modeles
    results = bayes_search.cv_results_
    top_5_indices = np.argsort(results['mean_test_score'])[-5:][::-1]
    top_5_params = [results['params'][i] for i in top_5_indices]

    # Entrainer les modeles
    def train_single_model(params, model_class, X_tr, Y_tr, model_id):
        m = model_class(**params)
        m.fit(X_tr, Y_tr)
        return (f'model_{model_id}', m)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(train_single_model, params, model.__class__, X_train, Y_train, i+1)
            for i, params in enumerate(top_5_params)
        ]
        top_5_models = [future.result() for future in futures]

    # 
    voting_model = VotingClassifier(estimators=top_5_models, voting='soft')
    voting_model.fit(X_train, Y_train)

    # Créer l'objet de retour
    trained_model = model_entrainer()
    trained_model.model_fiter = voting_model
    trained_model.hyperparameters = {
        'top_5_params': top_5_params,
        'best_from_bayes': bayes_search.best_params_
    }

    # Predictions et metrics
    predictions = voting_model.predict(X_dev)
    report = classification_report(Y_dev, predictions, output_dict=True)
    if isinstance(report, dict):
        trained_model.metrics = report

    return trained_model
