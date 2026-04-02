from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from security import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_admin():
  db: Session = SessionLocal()

  try:
    # ADMIN
    admin = db.query(User).filter(
      (User.email == "ali.dinarbous58@gmail.com") |
      (User.username == "Alidinarbous")
    ).first()

    if admin:
      logger.info("Admin already exists")
    else:
      new_admin = User(
        username="Alidinarbous",
        email="ali.dinarbous58@gmail.com",
        hashed_password=get_password_hash("admin123"),
        is_admin=True,
        is_active=True
      )
      db.add(new_admin)
      logger.info("Admin created")

    # TEST USER
    user = db.query(User).filter(User.username == "testuser").first()

    if not user:
      test_user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("test123"),
        is_admin=False,
        is_active=True
      )
      db.add(test_user)
      logger.info("Test user created")

    # un seul commit
    db.commit()

  except Exception as e:
    logger.error(f"Error: {e}")
    db.rollback()

  finally:
    db.close()


if __name__ == "__main__":
  create_admin()