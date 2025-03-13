# my-facade-api/app.py
import os
from fastapi import FastAPI
from dotenv import load_dotenv
from src.presentation.collateral_router import router as collateral_router

load_dotenv()

app = FastAPI()

app.include_router(collateral_router, prefix="/collateral")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
