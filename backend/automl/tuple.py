from argparse import BooleanOptionalAction
from typing import List, Any, Optional
from enum import Enum
import data_info as Di
from sklearn.pipeline import Pipeline

class type_enum(str, Enum):
    MULTICLASS = "multiclass"
    MULTILABEL = "multilabel"
    BINARY_CLASSIFICATION = "classification_binaire"
    REGRESSION = "regression"
    NONE = "none"


    
class Data_set:
    """Classe pour stocker les données d'entraînement, de développement et de test."""
    
    def __init__(
        self,
        X_train: List[List[Any]],
        Y_train: List[List[Any]],
        X_dev: List[List[Any]],
        Y_dev: List[List[Any]],
        X_test: List[List[Any]],
        Y_test: List[List[Any]],
        type_problem: 'type_enum',
        equilibre_labels: bool|None,
        preprocessing_pipeline: Pipeline
    ):
        self.X_train = X_train
        self.Y_train = Y_train
        self.X_dev = X_dev
        self.Y_dev = Y_dev
        self.X_test = X_test
        self.Y_test = Y_test
        self.type_probleme = type_problem
        self.equilibre_labels = equilibre_labels
        self.preprocessing_pipeline = preprocessing_pipeline



