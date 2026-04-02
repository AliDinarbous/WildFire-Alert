import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_admin_user
from predictor import predictor
import crud, schemas, models

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/train", response_model=schemas.ModelVersionResponse)
def train(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    try:
        file_bytes = file.file.read()
        info = predictor.train(file_bytes, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    crud.deactivate_all_models(db)
    versions = crud.get_all_models(db)
    new_version = f"v{len(versions) + 1}"

    model_data = schemas.ModelVersionCreate(
        model_type=info.get("model_type", "unknown"),
        version=new_version,
        model_path="/app/data/model/wildfire_model.pkl",
        dataset_path="uploaded"
    )
    return crud.create_model_version(db, model_data)


@router.get("/eval")
def evaluate(current_user: models.User = Depends(get_current_admin_user)):
    try:
        return predictor.evaluate()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/models/versions", response_model=list[schemas.ModelVersionResponse])
def get_versions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    return crud.get_all_models(db)


@router.put("/models/reset")
def reset_model(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    crud.deactivate_all_models(db)
    return {"message": "Modèle réinitialisé"}