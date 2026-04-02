import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.model_selection import cross_val_score
from sklearn.multioutput import MultiOutputClassifier
from tuple import Data_set, type_enum


def model_selector(dataset: Data_set):
    """
    Args:
        dataset: donnée de type Dataset contenant les données d'entraînement de dev et de test 
                 ainsi que les informations sur le type de problème (régression ou classification).
    Returns:
        best_model: le modèle ML sélectionné comme étant le plus performant pour le dataset donné.
    """

    models = []
    
    match dataset.type_probleme:
        case type_enum.BINARY_CLASSIFICATION:
            models = [
                RandomForestClassifier(),
                GradientBoostingClassifier(),
            ]
        case type_enum.MULTICLASS:
            models = [
                RandomForestClassifier(),
                GradientBoostingClassifier(),
            ]
        case type_enum.MULTILABEL:
            models = [
                MultiOutputClassifier(RandomForestClassifier()),
                MultiOutputClassifier(GradientBoostingClassifier()),
        
            ]
        case type_enum.REGRESSION:
            models = [
                RandomForestRegressor(),
                GradientBoostingRegressor(),
            ]
        case _:
            raise ValueError("Type de problème non pris en charge ou non spécifié.")
        
    best_score = -np.inf
    best_model = None
    
    # Convertir les listes en numpy arrays pour compatibilité avec scikit-learn
    X_train = np.array(dataset.X_train)
    Y_train_raw = np.array(dataset.Y_train)
    
    # Adapter le format de Y_train selon le type de problème
    if dataset.type_probleme == type_enum.MULTILABEL:
        # Pour multilabel, garder la forme 2D
        Y_train = Y_train_raw
    elif dataset.type_probleme == type_enum.MULTICLASS:
        # Pour multiclass : si one-hot encoding (plusieurs colonnes), convertir en indices
        if Y_train_raw.ndim == 2 and Y_train_raw.shape[1] > 1:
            Y_train = np.argmax(Y_train_raw, axis=1)
        elif Y_train_raw.ndim == 2 and Y_train_raw.shape[1] == 1:
            Y_train = Y_train_raw.ravel()
        else:
            Y_train = Y_train_raw
    else:
        # Pour les autres cas (classification binaire, régression)
        # Si Y_train a une seule colonne, l'aplatir en 1D
        if Y_train_raw.ndim == 2 and Y_train_raw.shape[1] == 1:
            Y_train = Y_train_raw.ravel()
        else:
            Y_train = Y_train_raw
    
    # Déterminer la métrique de scoring selon le type de problème
    classification_types = [
        type_enum.BINARY_CLASSIFICATION, 
        type_enum.MULTICLASS, 
        type_enum.MULTILABEL
    ]
    scoring = 'accuracy' if dataset.type_probleme in classification_types else 'neg_mean_squared_error'
    
    # Fonction pour obtenir le nom complet du modèle
    def get_model_name(model):
        name = type(model).__name__
        # Pour MultiOutputClassifier, afficher aussi le classifieur sous-jacent
        if hasattr(model, 'estimator'):
            inner_name = type(model.estimator).__name__
            return f"{name}({inner_name})"
        return name
    
    # Entraîner les modèles séquentiellement pour éviter les deadlocks
    print(f"Training {len(models)} models...")
    for i, model in enumerate(models):
        model_name = get_model_name(model)
        print(f"  [{i+1}/{len(models)}] Training {model_name}...", end=" ", flush=True)
        try:
            scores = cross_val_score(model, X_train, Y_train, cv=5, scoring=scoring, n_jobs=1)
            avg_score = np.mean(scores)
            print(f"Score: {avg_score:.4f}")
            
            if avg_score > best_score:
                best_score = avg_score
                best_model = model
        except Exception as e:
            print(f"Error: {e}")
            continue

    # Vérifier qu'un modèle a été sélectionné
    if best_model is None:
        raise RuntimeError("No model could be selected.")
    
    print(f"\nBest model: {get_model_name(best_model)} (score: {best_score:.4f})")
    
    return best_model