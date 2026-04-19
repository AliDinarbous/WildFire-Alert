from typing import Any, Optional
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import RidgeClassifier
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor

from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.multioutput import MultiOutputClassifier
from trainer.model import model_entrainer 
from tuple import type_enum


from trainer.rf_classification import rf_trainer
from trainer.rf_regression import rfr_trainer
from trainer.gboost_classification import gbc_trainer
from trainer.gboost_regression import gbr_trainer


def gnb_trainer(model, dataset) -> model_entrainer:
    """
    Entraîne un modèle GaussianNB et retourne le modèle entraîné.
    GaussianNB n'a pas d'hyperparamètres à optimiser, donc on l'entraîne directement.
    
    Args:
        model: Le modèle GaussianNB à entraîner
        dataset: Le dataset contenant les données d'entraînement et de validation
        
    Returns:
        trained_model: Le modèle GaussianNB entraîné
    """
    from sklearn.metrics import confusion_matrix
    import numpy as np
    
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
    
    model.fit(X_train, Y_train)
    
    trained_model = model_entrainer()
    trained_model.model_fiter = model
    trained_model.hyperparameters = {"var_smoothing": model.var_smoothing}
    
    predictions = model.predict(X_dev)
    trained_model.confusion_matrix = confusion_matrix(Y_dev, predictions)
    
    return trained_model


def ridge_trainer(model, dataset) -> model_entrainer:
    """
    Entraîne un modèle RidgeClassifier avec recherche d'hyperparamètres.
    
    Args:
        model: Le modèle RidgeClassifier à entraîner
        dataset: Le dataset contenant les données d'entraînement et de validation
        
    Returns:
        trained_model: Le modèle RidgeClassifier entraîné avec les meilleurs hyperparamètres
    """
    from sklearn.metrics import confusion_matrix
    import numpy as np
    
    param_grid = {
        'alpha': [0.01, 0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0],
        'fit_intercept': [True, False],
        'solver': ['auto', 'svd', 'cholesky', 'lsqr', 'sparse_cg', 'sag', 'saga']
    }
    
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
    
    grid_search = GridSearchCV(model, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
    grid_search.fit(X_train, Y_train)
    
    trained_model = model_entrainer()
    trained_model.model_fiter = grid_search.best_estimator_
    trained_model.hyperparameters = grid_search.best_params_
    
    predictions = trained_model.model_fiter.predict(X_dev)
    trained_model.confusion_matrix = confusion_matrix(Y_dev, predictions)
    
    return trained_model


def train_model(model, dataset) -> Optional[model_entrainer]:
    """
    Entraîne le modèle donné sur le dataset fourni et retourne le modèle entraîné.
    
    Args:
        model: Le modèle à entraîner
        dataset: Le dataset contenant les données d'entraînement et de validation
        
    Returns:
        best_model: Le modèle entraîné avec les meilleurs hyperparamètres
    """
    
    trainded_model : Optional[model_entrainer] = None
    match model:

        case RandomForestClassifier():
            trainded_model = rf_trainer(model, dataset)
        case GradientBoostingClassifier():
            trainded_model = gbc_trainer(model, dataset)
        case RandomForestRegressor():
            trainded_model = rfr_trainer(model, dataset)
        case GradientBoostingRegressor():
            trainded_model = gbr_trainer(model, dataset)
        case _:
            # Fallback: entraîner le modèle directement sans recherche d'hyperparamètres
            trainded_model = default_trainer(model, dataset)
    
    return trainded_model


def default_trainer(model, dataset) -> model_entrainer:
    """
    Trainer par défaut pour les modèles non supportés.
    Entraîne le modèle directement sans recherche d'hyperparamètres.
    """
    import numpy as np
    from sklearn.metrics import confusion_matrix
    from automl.tuple import type_enum
    
    X_train = np.array(dataset.X_train)
    Y_train_raw = np.array(dataset.Y_train)
    X_dev = np.array(dataset.X_dev)
    Y_dev_raw = np.array(dataset.Y_dev)
    
    # Adapter le format de Y selon le type de problème
    if dataset.type_probleme == type_enum.MULTILABEL:
        # Pour multilabel, garder la forme 2D
        Y_train = Y_train_raw
        Y_dev = Y_dev_raw
    elif dataset.type_probleme == type_enum.MULTICLASS:
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
        # Pour les autres cas (classification binaire, régression)
        if Y_train_raw.ndim == 2 and Y_train_raw.shape[1] == 1:
            Y_train = Y_train_raw.ravel()
            Y_dev = Y_dev_raw.ravel()
        else:
            Y_train = Y_train_raw
            Y_dev = Y_dev_raw
    
    # Entraîner le modèle
    model.fit(X_train, Y_train)
    
    trained_model = model_entrainer()
    trained_model.model_fiter = model
    trained_model.hyperparameters = {"note": "Entraîné sans recherche d'hyperparamètres"}
    
    # Calculer les prédictions et la matrice de confusion si possible
    try:
        predictions = model.predict(X_dev)
        # Pour multilabel, on calcule une confusion matrix par label ou on stocke None
        if dataset.type_probleme == type_enum.MULTILABEL:
            trained_model.confusion_matrix = None  # Pas de confusion matrix simple pour multilabel
        else:
            trained_model.confusion_matrix = confusion_matrix(Y_dev, predictions)
    except Exception:
        trained_model.confusion_matrix = None
    
    return trained_model

