import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers.webhooks import router as webhooks_router

if not os.environ.get("DOPPLER_TOKEN"):
    load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://([a-zA-Z0-9-]+\.)*afonsoingles\.dev(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": f"Hey!"}

@app.get("/health")
async def health():
    return {"status": "ok", "version": os.environ.get("APP_VERSION", "unknown"), "commit": os.environ.get("GIT_SHA", "unknown")}

app.include_router(webhooks_router, tags=["webhooks"])