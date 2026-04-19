from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil, os, zipfile
from automl import fit, eval, predict, save_model, load_model, get_model_info
import requests
from pathlib import Path
app = FastAPI()

MODEL_PATH = "/app/data/model/wildfire_model.pkl"
DATASET_DIR = "/app/data/dataset"

@app.on_event("startup")
def startup():
    if Path(MODEL_PATH).exists():
        load_model(MODEL_PATH)
        print("Modèle chargé au démarrage")


@app.get("/")
def root():
    return {"message": "AutoML running"}


@app.post("/train")
def train(file: UploadFile = File(...)):
    # Sauvegarder et dézipper le dataset
    os.makedirs(DATASET_DIR, exist_ok=True)
    zip_path = os.path.join(DATASET_DIR, file.filename)
    with open(zip_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    dataset_name = file.filename.replace(".zip", "")
    extract_path = os.path.join(DATASET_DIR, dataset_name)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)
    os.remove(zip_path)

    # Entraîner et sauvegarder
    try:
        fit(extract_path)
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        save_model(MODEL_PATH)
        return get_model_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/eval")
def evaluate():
    try:
        metrics = eval()
        if "confusion_matrix" in metrics:
            metrics["confusion_matrix"] = metrics["confusion_matrix"].tolist()
        return metrics
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/predict")
def predict_city(city: str):
    try:
        import math
        # Coordonnées
        geo = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json", "limit": 1},
            headers={"User-Agent": "WildFireAlert/1.0"}
        ).json()
        if not geo:
            raise HTTPException(status_code=404, detail="Ville introuvable")
        lat, lon = float(geo[0]["lat"]), float(geo[0]["lon"])

        # Tuile satellite
        zoom = 15
        n = 2 ** zoom
        x = int((lon + 180) / 360 * n)
        y = int((1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n)
        url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/15/{y}/{x}"
        response = requests.get(url)

        proba = predict(response)
        return {
            "city": city,
            "latitude": lat,
            "longitude": lon,
            "fire_probability": round(proba, 4),
            "risk_level": _risk_level(proba)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model/info")
def model_info():
    return get_model_info()


def _risk_level(proba: float) -> str:
    if proba < 0.3:
        return "LOW"
    elif proba < 0.6:
        return "MEDIUM"
    elif proba < 0.8:
        return "HIGH"
    return "CRITICAL"