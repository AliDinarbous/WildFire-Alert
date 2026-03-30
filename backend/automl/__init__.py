# AutoML Package
# Utilisation simple : fit("path_to_data") puis eval() puis predict("path_to_test")

from automl.automl import fit, eval, predict, save_model, load_model, get_model_info

__all__ = [
    'fit',
    'eval',
    'predict',
    'save_model',
    'load_model',
    'get_model_info',
]

__version__ = "0.1.0"
