import pytest
from fastapi.testclient import TestClient
import sys
import os
from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API running"}


def test_login_invalid_credentials():
    response = client.post(
        "/auth/login",
        data={"username": "fakeuser", "password": "fakepassword"}
    )
    assert response.status_code == 401


def test_predict_without_token():
    response = client.post("/predict/", json={"city": "Paris"})
    assert response.status_code == 401


def test_admin_train_without_token():
    response = client.post("/admin/train")
    assert response.status_code == 401


def test_admin_eval_without_token():
    response = client.get("/admin/eval")
    assert response.status_code == 401


def test_register_missing_fields():
    response = client.post("/auth/register", json={"username": "test"})
    assert response.status_code == 422