from fastapi import FastAPI
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

app = FastAPI(root_path="/api")

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

@app.get("/healthy")
def get_status():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = "connected"
    except OperationalError:
        db_status = "disconnected"

    return {
        "status": "success",
        "backend": "online",
        "database": db_status
    }