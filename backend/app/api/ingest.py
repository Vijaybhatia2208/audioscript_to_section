from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.parser.srt_parser import parse_srt
from app.parser.vtt_parser import parse_vtt
from app.chunking.chunker import create_subtitle_chunks
from app.embeddings.embedding_service import EmbeddingService
from app.vector_db.qdrant import QdrantService

router = APIRouter()


class IngestRequest(BaseModel):
    file_or_dir_path: str
    chunk_duration_sec: Optional[float] = 45.0
    overlap_duration_sec: Optional[float] = 10.0


def ingest_path(target_path: str, chunk_duration_sec: float = 45.0, overlap_duration_sec: float = 10.0) -> Dict[str, Any]:
    """
    Local ingestion pipeline function:
    1. Scans file or directory for .srt and .vtt subtitle files.
    2. Parses metadata, module, lesson, and time-stamped cues.
    3. Chunks cues into time-windowed segments.
    4. Generates embeddings and upserts into Qdrant.
    """
    path = Path(target_path)
    if not path.exists():
        raise FileNotFoundError(f"Target path does not exist: {target_path}")

    files_to_process = []
    if path.is_file():
        if path.suffix.lower() in [".srt", ".vtt"]:
            files_to_process.append(path)
    elif path.is_dir():
        for ext in ["*.srt", "*.vtt"]:
            files_to_process.extend(path.rglob(ext))

    if not files_to_process:
        return {
            "status": "error",
            "message": f"No .srt or .vtt subtitle files found at path: {target_path}",
            "processed_files": 0,
            "total_chunks": 0
        }

    all_chunks = []
    for file_p in files_to_process:
        str_path = str(file_p)
        if file_p.suffix.lower() == ".srt":
            cues = parse_srt(str_path)
        else:
            cues = parse_vtt(str_path)
            
        chunks = create_subtitle_chunks(
            cues,
            target_duration_sec=chunk_duration_sec,
            overlap_duration_sec=overlap_duration_sec
        )
        all_chunks.extend(chunks)

    if not all_chunks:
        return {
            "status": "warning",
            "message": "Files parsed successfully but 0 chunks were produced.",
            "processed_files": len(files_to_process),
            "total_chunks": 0
        }

    # Generate Embeddings & Store in Qdrant
    embedder = EmbeddingService()
    chunk_texts = [c["text"] for c in all_chunks]
    embeddings = embedder.embed_documents(chunk_texts)

    qdrant = QdrantService()
    upserted_count = qdrant.upsert_chunks(all_chunks, embeddings)

    return {
        "status": "success",
        "processed_files": len(files_to_process),
        "total_chunks": len(all_chunks),
        "upserted_vectors": upserted_count,
        "sample_chunk": all_chunks[0] if all_chunks else None
    }


@router.post("/ingest")
async def ingest_subtitles_endpoint(request: IngestRequest):
    """
    FastAPI Ingestion Endpoint.
    NOTE: API call logic is currently commented out as requested so testing can be done on local files first.
    """
    # =========================================================================
    # API ENDPOINT CALL COMMENTED OUT FOR LOCAL PATH TESTING
    # =========================================================================
    # try:
    #     result = ingest_path(
    #         target_path=request.file_or_dir_path,
    #         chunk_duration_sec=request.chunk_duration_sec,
    #         overlap_duration_sec=request.overlap_duration_sec
    #     )
    #     return result
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
    # =========================================================================

    return {
        "status": "disabled",
        "message": "API endpoint logic is commented out for local device testing. Use test_ingest_local.py or direct Python execution."
    }
