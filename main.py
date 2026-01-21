import os
from fastapi import FastAPI
from dotenv import load_dotenv
from routers.webhooks import router as webhooks_router

if not os.environ.get("DOPPLER_TOKEN"):
    load_dotenv()

app = FastAPI()


@app.get("/")
async def root():
    return {"message": f"Hey! The doppler testing var is: {os.environ.get('DOPPLER_TEST')}"}

@app.get("/health")
async def health():
    return {"status": "ok", "version": os.environ.get("APP_VERSION", "unknown"), "commit": os.environ.get("GIT_SHA", "unknown")}

app.include_router(webhooks_router, tags=["webhooks"])