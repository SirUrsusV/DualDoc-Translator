"""Точка входа FastAPI-приложения."""
from fastapi import FastAPI

app = FastAPI(title="DualDoc Translator API", version="0.1.0")

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
