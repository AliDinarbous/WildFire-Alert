from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from datetime import datetime

from database import Base


class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True, index=True)

  username = Column(String, unique=True, index=True, nullable=False)  
  email = Column(String, unique=True, index=True, nullable=False)

  hashed_password = Column(String, nullable=False)

  is_admin = Column(Boolean, default=False)
  is_active = Column(Boolean, default=True)

  created_at = Column(DateTime(timezone=True), server_default=func.now())


class ModelVersion(Base):
  __tablename__ = "model_versions"

  id = Column(Integer, primary_key=True, index=True)

  model_type = Column(String)
  version = Column(String)

  model_path = Column(String)
  dataset_path = Column(String)

  created_at = Column(DateTime, default=datetime.utcnow)
  is_active = Column(Boolean, default=True)