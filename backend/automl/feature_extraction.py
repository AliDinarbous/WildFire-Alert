import os
import numpy as np
import pandas as pd
import cv2
from skimage.feature import graycomatrix
from scipy.stats import skew, kurtosis
from concurrent.futures import ProcessPoolExecutor


DATASET_PATH = os.getenv("DATASET_PATH", "backend/automl/data/dataset")

TRAIN_LIMIT = 4000
OTHER_LIMIT = 850
MIN_IMAGE_SIZE = 8


# Recuperer le chemin vers train, dev, test

def find_splits(dataset_path):

    root = os.path.join(dataset_path, os.listdir(dataset_path)[0])
    splits = os.listdir(root)

    train = [s for s in splits if "train" in s.lower()][0]
    test  = [s for s in splits if "test"  in s.lower()][0]
    dev   = [s for s in splits if s not in [train, test]][0]

    return (
        os.path.join(root, train),
        os.path.join(root, test),
        os.path.join(root, dev)
    )

# recuperer les images 0 et image 1
def get_class_dirs(split_path):

    dirs = os.listdir(split_path)

    no_fire = [d for d in dirs if "no" in d.lower()][0]
    fire = [d for d in dirs if d != no_fire][0]

    return fire, no_fire


