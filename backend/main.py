from fastapi import FastAPI
from app.api import ingest, chat, yt_router

app = FastAPI(title="YouTube & Course Subtitle RAG Backend")

app.include_router(ingest.router, prefix="/api", tags=["Ingest"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(yt_router.router, prefix="/api", tags=["YouTube RAG"])


@app.get("/")
def read_root():
    return {"message": "YouTube & Course Subtitle RAG API is running"}

