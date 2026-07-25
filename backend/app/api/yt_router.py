from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.yt.yt_service import YouTubeRAGService

router = APIRouter()
yt_service = YouTubeRAGService()


class YouTubeIngestRequest(BaseModel):
    url_or_id: str = Field(..., description="YouTube Video URL or Video ID", example="https://www.youtube.com/watch?v=bMknfKXIFA8")
    chunk_duration_sec: Optional[float] = Field(default=45.0, description="Target chunk duration in seconds")


class YouTubeChatRequest(BaseModel):
    url_or_id: str = Field(..., description="YouTube Video URL or Video ID", example="https://www.youtube.com/watch?v=bMknfKXIFA8")
    query: str = Field(..., description="User question string", example="What is state in React?")
    limit: Optional[int] = Field(default=5, description="Top-K context chunks to retrieve", ge=1, le=20)


class YouTubeTranscriptRequest(BaseModel):
    url_or_id: str = Field(..., description="YouTube Video URL or Video ID", example="https://www.youtube.com/watch?v=bMknfKXIFA8")
    languages: Optional[List[str]] = Field(default=["en"], description="Preferred subtitle languages")


@router.post("/yt/transcript")
async def get_youtube_transcript_endpoint(request: YouTubeTranscriptRequest):
    """
    Fetches the complete timestamped transcript and video metadata for a YouTube URL.

    Inputs:
    - url_or_id: YouTube URL or 11-character Video ID.

    Returns:
    - video_id, embed_url, thumbnail_url, total_duration_str, cue_count, and array of timecoded cues.
    """
    try:
        from app.parser.yt_parser import get_youtube_video_info
        info = get_youtube_video_info(request.url_or_id, languages=request.languages or ["en"])
        return info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/yt/ingest")
async def ingest_youtube_video_endpoint(request: YouTubeIngestRequest):
    """
    Ingests a YouTube video transcript into Qdrant vector database.
    """
    try:
        result = yt_service.ingest_youtube_video(
            url_or_id=request.url_or_id,
            target_duration_sec=request.chunk_duration_sec or 45.0
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/yt/chat")
@router.post("/yt/query")
async def chat_youtube_video_endpoint(request: YouTubeChatRequest):
    """
    Executes a grounded RAG query over a specific YouTube video.
    Auto-ingests the video transcript if not already stored in Qdrant.
    Returns answer with timestamp citations for 1-click video seeking.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    try:
        result = yt_service.chat_with_youtube_video(
            video_id_or_url=request.url_or_id,
            query=request.query,
            limit=request.limit or 5
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


