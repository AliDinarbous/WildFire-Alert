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


# Charger l'image et verifier sa taille puis inverser bgr en rgb

def read_bands(path):

    img = cv2.imread(path, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError(f"Impossible de lire : {path}")

    h, w = img.shape[:2]
    if h < MIN_IMAGE_SIZE or w < MIN_IMAGE_SIZE:
        raise ValueError(f"Image trop petite : {path}")

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    return np.transpose(rgb, (2, 0, 1))


# calculer les indices spectreaux

def spectral_indices(b):

    r, g, b = b
    eps = 1e-6

    exg = 2*g - r - b
    vci = (g - r) / (g + r + b + eps)
    rg_ratio = np.clip(r/(g+eps), 0, 10)
    brightness = (r+g+b)/3

    rgb = (np.stack([r,g,b],axis=-1)*255).astype(np.uint8)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)

    hue = hsv[...,0]/179
    sat = hsv[...,1]/255

    veg_ratio  = np.mean((hue>0.33)&(hue<0.84))
    bare_ratio = np.mean((sat<0.2)&(brightness>0.4))

    return {
        "exg":exg,
        "vci":vci,
        "rg_ratio":rg_ratio,
        "brightness":brightness,
        "saturation":sat,
        "_veg_ratio":veg_ratio,
        "_bare_ratio":bare_ratio
    }


# calculer les stats des indices spectreaux

def stats(a):

    x = a.flatten()

    return {
        "mean":float(np.mean(x)),
        "std":float(np.std(x)),
        "min":float(np.min(x)),
        "max":float(np.max(x)),
        "p25":float(np.percentile(x,25)),
        "p75":float(np.percentile(x,75)),
        "skewness":float(skew(x)),
        "kurtosis":float(kurtosis(x))
    }


# recuperer les textures de l'image

def texture_features(gray):

    gray = (gray//4).astype(np.uint8)

    glcm = graycomatrix(
        gray,
        distances=[1],
        angles=[0,np.pi/4],
        levels=64,
        symmetric=True,
        normed=True
    )

    glcm = glcm[:,:,0,:].mean(axis=-1)

    i,j = np.ogrid[0:64,0:64]

    contrast = float(np.sum(glcm*(i-j)**2))
    energy = float(np.sum(glcm**2))
    homogeneity = float(np.sum(glcm/(1+np.abs(i-j))))

    mu_i = np.sum(i*glcm)
    mu_j = np.sum(j*glcm)

    sigma_i = np.sqrt(np.sum(glcm*(i-mu_i)**2)+1e-6)
    sigma_j = np.sqrt(np.sum(glcm*(j-mu_j)**2)+1e-6)

    corr = float(np.sum(glcm*(i-mu_i)*(j-mu_j))/(sigma_i*sigma_j))

    return {
        "tex_contrast":contrast,
        "tex_energy":energy,
        "tex_homogeneity":homogeneity,
        "tex_correlation":corr
    }


# extraire les indices spectreaux et les textures de l'image

def extract_features(args):

    path, label = args

    try:
        bands = read_bands(path)
    except ValueError:
        return None

    features = {}
    indices = spectral_indices(bands)

    for name,val in indices.items():

        if name.startswith("_"):
            features[name[1:]] = float(val)
            continue

        for k,v in stats(val).items():
            features[f"{name}_{k}"] = v

    for i,c in enumerate(["r","g","b"]):
        for k,v in stats(bands[i]).items():
            features[f"ch_{c}_{k}"] = v

    gray = cv2.cvtColor(
        (np.transpose(bands,(1,2,0))*255).astype(np.uint8),
        cv2.COLOR_RGB2GRAY
    )

    features.update(texture_features(gray))

    edges = cv2.Canny(gray,50,150)
    features["edge_density"] = float(np.mean(edges>0))

    features["target"] = label

    return features


# traiter le dataset entier

def collect_images(folder,label,limit):

    files = sorted([
        f for f in os.listdir(folder)
        if f.lower().endswith((".jpg",".jpeg"))
    ])

    files = files[:limit] if len(files)>limit else files

    return [(os.path.join(folder,f),label) for f in files]


def process_split(split_path,limit):

    fire,no_fire = get_class_dirs(split_path)

    fire_imgs = collect_images(os.path.join(split_path,fire),1,limit//2)
    no_fire_imgs = collect_images(os.path.join(split_path,no_fire),0,limit//2)

    imgs = fire_imgs + no_fire_imgs

    with ProcessPoolExecutor() as ex:
        rows = list(ex.map(extract_features,imgs))

    rows = [r for r in rows if r is not None]

    return pd.DataFrame(rows)


def build_datasets(dataset_path=DATASET_PATH):

    train,test,dev = find_splits(dataset_path)

    train_df = process_split(train,TRAIN_LIMIT)
    test_df  = process_split(test,OTHER_LIMIT)
    dev_df   = process_split(dev,OTHER_LIMIT)

    return train_df,test_df,dev_df