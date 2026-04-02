from sqlalchemy.orm import Session
import models
import schemas

def get_user_by_username(db: Session, username: str):
  return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
  return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
  db_user = models.User(
    username=user.username,
    email=user.email,
    hashed_password=hashed_password,
    is_admin=False
  )
  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user


def create_model_version(db: Session, model: schemas.ModelVersionCreate):
  db_model = models.ModelVersion(
    model_type=model.model_type,
    version=model.version,
    model_path=model.model_path,
    dataset_path=model.dataset_path,
    is_active=True
  )
  db.add(db_model)
  db.commit()
  db.refresh(db_model)
  return db_model


def get_all_models(db: Session):
  return db.query(models.ModelVersion).all()


def get_active_model(db: Session):
  return db.query(models.ModelVersion)\
           .filter(models.ModelVersion.is_active == True)\
           .first()


def deactivate_all_models(db: Session):
  db.query(models.ModelVersion)\
    .update({models.ModelVersion.is_active: False})
  db.commit()