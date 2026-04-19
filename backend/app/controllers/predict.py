from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from predictor import predictor
import models
import schemas

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("/")
def predict_fire_risk(
    request: schemas.PredictionRequest,
    current_user: models.User = Depends(get_current_user)
):
    try:
        result = predictor.predict_city(request.city)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))