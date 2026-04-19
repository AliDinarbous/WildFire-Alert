from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
  username: str
  email: EmailStr
  password: str


class UserLogin(BaseModel):
  username: str   
  password: str


class UserResponse(BaseModel):
  id: int
  username: str
  email: str
  is_admin: bool

  class Config:
    from_attributes = True


class Token(BaseModel):
  access_token: str
  token_type: str


class ModelVersionCreate(BaseModel):
  model_type: str
  version: str
  model_path: str
  dataset_path: str | None = None


class ModelVersionResponse(BaseModel):
  id: int
  model_type: str
  version: str
  model_path: str
  dataset_path: str | None
  is_active: bool
  created_at: datetime

  class Config:
    from_attributes = True



class PredictionRequest(BaseModel):
  city: str


class PredictionResponse(BaseModel):
    city: str
    latitude: float
    longitude: float
    fire_probability: float
    risk_level: str