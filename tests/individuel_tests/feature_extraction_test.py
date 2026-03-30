import os
import numpy as np
import pandas as pd
import cv2
import pytest
from backend.automl.feature_extraction import (
    find_splits,
    get_class_dirs,
    read_bands,
    spectral_indices,
    stats,
    texture_features,
    build_datasets
)


# creer des images et la structure du dataset attendu par le pipeline pour les tests

def create_fake_jpg(path, height=32, width=32):
    data = np.random.randint(30, 225, (height, width, 3), dtype=np.uint8)
    cv2.imwrite(str(path), data)


def create_dataset_structure(tmp_path, fire_name="fire", no_fire_name="no_fire",dev_name="dev", n_fire=2, n_no_fire=2):

    root = tmp_path / "dataset"
    ds = root / "wildfire_dataset"

    for split_name in ["train", "test", dev_name]:
        fire_dir    = ds / split_name / fire_name
        no_fire_dir = ds / split_name / no_fire_name

        fire_dir.mkdir(parents=True)
        no_fire_dir.mkdir(parents=True)

        for i in range(n_fire):
            create_fake_jpg(fire_dir / f"fire_{i}.jpg")
        for i in range(n_no_fire):
            create_fake_jpg(no_fire_dir / f"no_fire_{i}.jpg")

    return root


# teste: recuperer chemin vers train, dev, test ou train, val, test

def test_find_splits(tmp_path):
    
    dataset_root = create_dataset_structure(tmp_path)

    train, test, dev = find_splits(str(dataset_root))

    assert "train" in train
    assert "test" in test
    assert "dev" in dev

    assert os.path.exists(train), f"Le dossier train n'existe pas : {train}"
    assert os.path.exists(test),  f"Le dossier test n'existe pas : {test}"
    assert os.path.exists(dev),   f"Le dossier dev n'existe pas : {dev}"

    assert len({train, test, dev}) == 3, "train, test et dev ne doivent pas pointer vers le même dossier"


def test_find_splits_with_val(tmp_path):

    dataset_root = create_dataset_structure(tmp_path, dev_name="val")

    train, test, dev = find_splits(str(dataset_root))

    assert "train" in train
    assert "test" in test
    assert os.path.exists(dev)
    assert dev not in [train, test]


# recuperer les labels 1 et 0, pour les deux possibilites de nom de fichier

def test_get_class_dirs(tmp_path):
   
    dataset_root = create_dataset_structure(tmp_path)

    train_path = os.path.join(
        str(dataset_root),
        os.listdir(str(dataset_root))[0],
        "train"
    )

    fire, no_fire = get_class_dirs(train_path)

    assert "no" not in fire.lower(),  f"fire ne doit pas contenir 'no', obtenu : {fire}"
    assert "no" in no_fire.lower(),   f"no_fire doit contenir 'no', obtenu : {no_fire}"
    assert fire != no_fire


def test_get_class_dirs_wildfire_variant(tmp_path):
   
    dataset_root = create_dataset_structure(
        tmp_path, fire_name="wildfire", no_fire_name="no_wildfire"
    )

    train_path = os.path.join(
        str(dataset_root),
        os.listdir(str(dataset_root))[0],
        "train"
    )

    fire, no_fire = get_class_dirs(train_path)

    assert "no" not in fire.lower()
    assert "no" in no_fire.lower()


# tester la lecture des bandes

def test_read_bands(tmp_path):
    
    img_path = tmp_path / "test.jpg"
    create_fake_jpg(img_path, height=32, width=32)

    bands = read_bands(str(img_path))

    assert isinstance(bands, np.ndarray), "read_bands doit retourner un np.ndarray"
    assert bands.shape == (3, 32, 32),    f"Shape attendu (3,32,32), obtenu {bands.shape}"
    assert bands.dtype == np.float32



def test_read_bands_invalid_path():
    """read_bands doit lever ValueError sur un chemin inexistant."""
    with pytest.raises(ValueError, match="Impossible de lire"):
        read_bands("/chemin/qui/nexiste/pas.jpg")


# -----------------------------
# Test indices spectraux
# -----------------------------

def _fake_rgb_bands(h=32, w=32):
    """Array float32 (3, H, W) simule des bandes RGB normalisées."""
    return (np.random.rand(3, h, w) * 0.8 + 0.1).astype(np.float32)


def test_spectral_indices_keys():
   
    indices = spectral_indices(_fake_rgb_bands())

    expected_keys = {"exg", "vci", "rg_ratio", "brightness", "saturation",
                     "_veg_ratio", "_bare_ratio"}
    assert set(indices.keys()) == expected_keys, (
        f"Clés attendues : {expected_keys}, obtenues : {set(indices.keys())}"
    )


def test_spectral_indices_shapes():
  
    H, W = 32, 32
    indices = spectral_indices(_fake_rgb_bands(H, W))

    for name in ["exg", "vci", "rg_ratio", "brightness", "saturation"]:
        assert indices[name].shape == (H, W), (
            f"{name} : shape attendu ({H},{W}), obtenu {indices[name].shape}"
        )

    for name in ["_veg_ratio", "_bare_ratio"]:
        val = indices[name]
        assert np.isscalar(val) or np.ndim(val) == 0, (
            f"{name} doit être un scalaire, obtenu shape {np.shape(val)}"
        )


# Test texture_features

def test_texture_features_keys():
    """texture_features doit retourner exactement les 4."""
    gray = np.random.randint(0, 255, (32, 32), dtype=np.uint8)

    tf = texture_features(gray)

    assert set(tf.keys()) == {"tex_contrast", "tex_energy", "tex_homogeneity", "tex_correlation"}


STAT_SUFFIXES = ["mean", "std", "min", "max", "p25", "p75", "skewness", "kurtosis"]


def test_build_datasets(tmp_path):
    """build_datasets doit retourner 3 DataFrames avec les bonnes colonnes et labels."""
    dataset_root = create_dataset_structure(tmp_path, n_fire=2, n_no_fire=2)

    train_df, test_df, dev_df = build_datasets(str(dataset_root))

    assert isinstance(train_df, pd.DataFrame)
    assert isinstance(test_df,  pd.DataFrame)
    assert isinstance(dev_df,   pd.DataFrame)

    for df, name in [(train_df, "train"), (test_df, "test"), (dev_df, "dev")]:
        labels = set(df["target"].unique())
        assert labels == {0, 1}, f"{name} : labels attendus {{0,1}}, obtenus {labels}"




