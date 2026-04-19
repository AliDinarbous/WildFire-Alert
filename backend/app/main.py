from fastapi import FastAPI
import models

from controllers.auth import router as auth_router
from controllers.admin import router as admin_router
from controllers.predict import router as predict_router

app = FastAPI()

# auth routes
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(predict_router)

@app.get("/")
def root():
  return {"message": "API running"}