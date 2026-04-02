from sklearn.model_selection import RandomizedSearchCV
from trainer.model import model_entrainer
from sklearn.ensemble import VotingRegressor
from skopt import BayesSearchCV
from skopt.space import Integer, Real, Categorical
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np
from tuple import Data_set, type_enum

def rfr_trainer (model, dataset):
    """
    Entraine un modele RandomForestRegressor avec recherche d'hyperparamètres en 3 étapes :
    1. RandomizedSearch sur n_estimators, max_features, max_depth
    2. RandomizedSearch sur min_samples_leaf, min_samples_split
    3. Bayesian Optimization pour trouver les 5 meilleurs
    4. Vote avec les 5 meilleurs modèles
    
    Args:
        model: Le modèle RandomForestRegressor à entraîner
        dataset: Le dataset contenant X_train, Y_train, X_dev, Y_dev
        
    Returns:
        trained_model: Objet model_entrainer avec le voting regressor
    """

    # Pour la regression, la metrique principale est le MSE (ou RMSE)
    scoring = 'neg_mean_squared_error'

    # Préparer les données et aplatir Y si nécessaire
    X_train = np.array(dataset.X_train)
    Y_train = np.array(dataset.Y_train)
    if Y_train.ndim == 2 and Y_train.shape[1] == 1:
        Y_train = Y_train.ravel()
    
    X_dev = np.array(dataset.X_dev)
    Y_dev = np.array(dataset.Y_dev)
    if Y_dev.ndim == 2 and Y_dev.shape[1] == 1:
        Y_dev = Y_dev.ravel()

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
        scoring=scoring,
        random_state=42,
        n_jobs=-1
    )
    random_search_1.fit(X_train, Y_train)
    
    best_params_step1 = random_search_1.best_params_

    # ETAPE 2: RandomizedSearch sur min_samples_leaf, min_samples_split 
    param_dist_2 = {
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
        scoring=scoring,
        random_state=42,
        n_jobs=-1
    )
    random_search_2.fit(X_train, Y_train)

    best_params_step2 = random_search_2.best_params_

    # ETAPE 3: Bayesian Optimization pour top 5
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

    # Recuperer les 5 meilleurs hyperparamètres
    results = bayes_search.cv_results_
    top_5_indices = np.argsort(results['mean_test_score'])[-5:][::-1]
    top_5_params = [results['params'][i] for i in top_5_indices]

    # Entrainer les cinq meilleurs modèles
    from concurrent.futures import ThreadPoolExecutor

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

    voting_model = VotingRegressor(estimators=top_5_models)

    voting_model.fit(X_train, Y_train)

    # Creer l'objet de retour
    trained_model = model_entrainer()
    trained_model.model_fiter = voting_model
    trained_model.hyperparameters = {
        'top_5_params': top_5_params,
        'best_from_bayes': bayes_search.best_params_
    }

    # Predictions et MSE
    predictions = voting_model.predict(X_dev)
    mse = mean_squared_error(Y_dev, predictions)
    mae = mean_absolute_error(Y_dev, predictions)
    r2 =  r2_score(Y_dev, predictions)
    trained_model.metrics = {"mse": mse,"mae": mae,"r2": r2}

    return trained_model
