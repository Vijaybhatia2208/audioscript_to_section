from fastapi import FastAPI
from app.api import ingest, chat

app = FastAPI(title="Course Subtitle RAG Backend")

app.include_router(ingest.router, prefix="/api", tags=["Ingest"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])


@app.get("/")
def read_root():
    return {"message": "Course Subtitle RAG API is running"}
