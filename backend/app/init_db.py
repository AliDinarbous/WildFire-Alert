from database import create_tables
import models  

def init_db():
  print("Creating tables...")
  create_tables()
  print("Tables created")

if __name__ == "__main__":
  init_db()