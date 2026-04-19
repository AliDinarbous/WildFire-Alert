from typing import Any, Optional, Dict
import numpy as np


class model_entrainer:
    """
    Classe pour stocker un modèle entraîné avec ses métadonnées.
    
    Attributs:
        model_fiter: le modèle entraîné
        hyperparameters: un dictionnaire des hyperparamètres utilisés pour entraîner le modèle
        confusion_matrix: la matrice de confusion du modèle entraîné
        metrics: dictionnaire optionnel de métriques supplémentaires
    """
    
    def __init__(self):
        self.model_fiter: Any = None
        self.hyperparameters: Optional[Dict[str, Any]] = None
        self.confusion_matrix: Optional[np.ndarray] = None
        self.metrics: Optional[Dict[str, Any]] = None