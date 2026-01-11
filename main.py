import os
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": f"Hey! The doppler testing var is: {os.environ.get('DOPPLER_TEST')}"}

@app.get("/health")
async def health():
    return {"status": "ok"}