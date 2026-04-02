import logging
import requests

logger = logging.getLogger(__name__)

AUTOML_URL = "http://automl:5050"


class WildfirePredictor:

    def train(self, file_bytes: bytes, filename: str) -> dict:
        resp = requests.post(
            f"{AUTOML_URL}/train",
            files={"file": (filename, file_bytes, "application/zip")}
        )
        resp.raise_for_status()
        return resp.json()

    def evaluate(self) -> dict:
        resp = requests.get(f"{AUTOML_URL}/eval")
        resp.raise_for_status()
        return resp.json()

    def predict_city(self, city_name: str) -> dict:
        resp = requests.post(f"{AUTOML_URL}/predict", params={"city": city_name})
        resp.raise_for_status()
        return resp.json()

    def get_info(self) -> dict:
        resp = requests.get(f"{AUTOML_URL}/model/info")
        resp.raise_for_status()
        return resp.json()


predictor = WildfirePredictor()