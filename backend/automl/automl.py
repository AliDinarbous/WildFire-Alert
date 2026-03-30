# ------------------------------------------------------------------------------------- #
# |                                   AutoML Pipeline                                  | #
# ------------------------------------------------------------------------------------- #
import pandas as pd
import numpy as np
import os
import requests
from typing import Tuple, Optional, Dict, Any
from automl.feature_extraction import build_datasets, extract_features_from_bytes
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, 
    f1_score, 
    mean_squared_error, 
    r2_score,
    classification_report,
    confusion_matrix
)
import joblib
from automl.tuple import Data_set, type_enum
from automl.select_model import model_selector
from automl.data_preparation import data_preparation
from automl.trainer.model_trainer import train_model


# Variable globale pour stocker l'état de l'AutoML
_automl_state: Dict[str, Any] = {
    "dataset": None,
    "best_model": None,
    "trained_model": None,
    "is_fitted": False
}


def fit(data_path: str, verbose: bool = False) -> Any:
    """
    Point d'entrée principal de l'AutoML.
    
    Args:
        data_path: Chemin vers le répertoire contenant les données
        verbose: Afficher les informations détaillées
        
    Returns:
        trained_model: Le modèle entraîné avec les meilleurs hyperparamètres
    """
    global _automl_state
    
    train_df, test_df, dev_df = build_datasets(data_path)
    if verbose:
        print(f"Train: {train_df.shape}, Test: {test_df.shape}, Dev: {dev_df.shape}")

    dataset = data_preparation(train_df, test_df, dev_df)
    if verbose:
        print(f"Training set size: {len(dataset.X_train)}")
        print(f"Validation set size: {len(dataset.X_dev)}")
        print(f"Test set size: {len(dataset.X_test)}")
        print(f"Problem type: {dataset.type_probleme}")
    
    # Sélection du meilleur modèle
    best_model = model_selector(dataset)
    if verbose:
        print(f"Best model selected: {type(best_model).__name__}")
    
    print("optimize model")
    # Entraînement fin du modèle avec recherche d'hyperparamètres
    trained_model = train_model(best_model, dataset)
    if verbose:
        print("Model training completed.")
        if trained_model and trained_model.hyperparameters:
            print(f"Optimal hyperparameters: {trained_model.hyperparameters}")
    
    # Sauvegarder l'état
    _automl_state["dataset"] = dataset
    _automl_state["best_model"] = best_model
    _automl_state["trained_model"] = trained_model
    _automl_state["is_fitted"] = True
    
    return trained_model


def eval(dataset: Optional[Data_set] = None, verbose: bool = False) -> Dict[str, Any]:
    """
    Fonction qui retourne les métriques d'évaluation du modèle sélectionné sur le jeu de test.
    
    Args:
        dataset: Le dataset à utiliser (optionnel, utilise le dernier dataset fitté sinon)
        verbose: Afficher les informations détaillées
        
    Returns:
        metrics: Un dictionnaire contenant les métriques d'évaluation.
    """
    global _automl_state
    
    if not _automl_state["is_fitted"]:
        raise RuntimeError("Le modèle n'a pas encore été entraîné. Appelez fit() d'abord.")
    
    if dataset is None:
        dataset = _automl_state["dataset"]
    
    if dataset is None:
        raise RuntimeError("Aucun dataset disponible.")
    
    trained_model = _automl_state["trained_model"]
    
    if trained_model is None or trained_model.model_fiter is None:
        raise RuntimeError("Aucun modèle entraîné disponible.")
    
    model = trained_model.model_fiter
    
    # Prédictions sur le jeu de test
    X_test = np.array(dataset.X_test)
    Y_test_raw = np.array(dataset.Y_test)
    
    # Adapter le format de Y_test selon le type de problème
    if dataset.type_probleme == type_enum.MULTILABEL:
        # Pour multilabel, garder la forme 2D
        Y_test = Y_test_raw
    elif dataset.type_probleme == type_enum.MULTICLASS:
        # Pour multiclass : si one-hot encoding, convertir en indices
        if Y_test_raw.ndim == 2 and Y_test_raw.shape[1] > 1:
            Y_test = np.argmax(Y_test_raw, axis=1)
        elif Y_test_raw.ndim == 2 and Y_test_raw.shape[1] == 1:
            Y_test = Y_test_raw.ravel()
        else:
            Y_test = Y_test_raw
    else:
        # Pour les autres cas (classification binaire, régression)
        if Y_test_raw.ndim == 2 and Y_test_raw.shape[1] == 1:
            Y_test = Y_test_raw.ravel()
        else:
            Y_test = Y_test_raw
    
    Y_pred = model.predict(X_test)
    
    metrics = {}
    
    classification_types = [
        type_enum.BINARY_CLASSIFICATION,
        type_enum.MULTICLASS,
        type_enum.MULTILABEL
    ]
    
    if dataset.type_probleme in classification_types:
        # Métriques de classification
        metrics["accuracy"] = accuracy_score(Y_test, Y_pred)
        metrics["f1_score_macro"] = f1_score(Y_test, Y_pred, average='macro', zero_division=0)
        metrics["f1_score_micro"] = f1_score(Y_test, Y_pred, average='micro', zero_division=0)
        
        # Matrice de confusion (seulement pour classification binaire et multiclass)
        if dataset.type_probleme != type_enum.MULTILABEL:
            metrics["confusion_matrix"] = confusion_matrix(Y_test, Y_pred)
        else:
            # Pour multilabel, on calcule les métriques par label
            from sklearn.metrics import multilabel_confusion_matrix
            metrics["confusion_matrix"] = multilabel_confusion_matrix(Y_test, Y_pred)
        
        metrics["classification_report"] = classification_report(Y_test, Y_pred, zero_division=0)
        
        if verbose:
            print(f"=== Classification Metrics ===")
            print(f"Accuracy: {metrics['accuracy']:.4f}")
            print(f"F1-Score (macro): {metrics['f1_score_macro']:.4f}")
            print(f"F1-Score (micro): {metrics['f1_score_micro']:.4f}")
            if dataset.type_probleme != type_enum.MULTILABEL:
                print(f"\nConfusion Matrix:\n{metrics['confusion_matrix']}")
            else:
                print(f"\nConfusion Matrices per label (multilabel):")
                print(f"Shape: {metrics['confusion_matrix'].shape}")
            print(f"\nClassification Report:\n{metrics['classification_report']}")
    else:
        # Métriques de régression
        metrics["mse"] = mean_squared_error(Y_test, Y_pred)
        metrics["rmse"] = np.sqrt(metrics["mse"])
        metrics["r2_score"] = r2_score(Y_test, Y_pred)
        
        if verbose:
            print(f"=== Regression Metrics ===")
            print(f"MSE: {metrics['mse']:.4f}")
            print(f"RMSE: {metrics['rmse']:.4f}")
            print(f"R² Score: {metrics['r2_score']:.4f}")
    
    return metrics


def predict(response: requests.Response, verbose: bool = True) -> float:
    """
    Fait une prédiction depuis une réponse HTTP contenant une image satellite JPG.

    Args:
        response : résultat de requests.get(url) — image satellite en bytes
        verbose  : afficher les informations détaillées

    Returns:
        proba_fire : probabilité d'incendie (float entre 0 et 1)
    """
    global _automl_state

    if not _automl_state["is_fitted"]:
        raise RuntimeError("Le modèle n'a pas encore été entraîné. Appelez fit() d'abord.")

    trained_model = _automl_state["trained_model"]

    if trained_model is None or trained_model.model_fiter is None:
        raise RuntimeError("Aucun modèle entraîné disponible.")

    #  Extraire les features depuis les bytes de l'image
    image_bytes = response.content
    X = extract_features_from_bytes(image_bytes)

    if verbose:
        print(f"Features extraites : {X.shape}")

    #Inférence predict_proba retourne [[proba_0, proba_1]]
    probas = trained_model.model_fiter.predict_proba(X)
    proba_fire = float(probas[0][1])  # probabilité du label 1 

    if verbose:
        print(f"Probabilité d'incendie : {proba_fire:.4f}")

    return proba_fire


def save_model(filepath: str) -> None:
    """
    Sauvegarde le modèle entraîné sur le disque.
    
    Args:
        filepath: Chemin du fichier de sauvegarde
    """
    global _automl_state
    
    if not _automl_state["is_fitted"]:
        raise RuntimeError("Le modèle n'a pas encore été entraîné. Appelez fit() d'abord.")
    
    joblib.dump(_automl_state, filepath)
    print(f"Modèle sauvegardé dans {filepath}")


def load_model(filepath: str, verbose: bool = True) -> None:
    """
    Charge un modèle précédemment sauvegardé.
    Après le chargement, vous pouvez utiliser predict() et eval() directement.
    
    Args:
        filepath: Chemin du fichier de sauvegarde
        verbose: Afficher les informations détaillées
    """
    global _automl_state
    
    _automl_state = joblib.load(filepath)
    
    if verbose:
        print(f"Modèle chargé depuis {filepath}")
        if _automl_state["is_fitted"]:
            trained_model = _automl_state["trained_model"]
            dataset = _automl_state["dataset"]
            print(f"Type de modèle: {type(trained_model.model_fiter).__name__}")
            print(f"Type de problème: {dataset.type_probleme.value if hasattr(dataset.type_probleme, 'value') else dataset.type_probleme}")
            if trained_model.hyperparameters:
                print(f"Hyperparamètres: {trained_model.hyperparameters}")
        else:
            print("Attention: Le modèle chargé n'est pas entraîné.")


def get_model_info() -> Dict[str, Any]:
    """
    Retourne les informations sur le modèle entraîné.
    
    Returns:
        info: Dictionnaire avec les informations du modèle
    """
    global _automl_state
    
    if not _automl_state["is_fitted"]:
        return {"is_fitted": False}
    
    trained_model = _automl_state["trained_model"]
    dataset = _automl_state["dataset"]
    
    return {
        "is_fitted": True,
        "model_type": type(trained_model.model_fiter).__name__ if trained_model else None,
        "hyperparameters": trained_model.hyperparameters if trained_model else None,
        "problem_type": dataset.type_probleme.value if dataset else None,
        "is_balanced": dataset.equilibre_labels if dataset else None
    }
    
    