import logging
from typing import List, Dict, Any, Optional

from app.parser.yt_parser import fetch_youtube_transcript, extract_youtube_video_id
from app.chunking.chunker import create_subtitle_chunks
from app.embeddings.embedding_service import EmbeddingService
from app.vector_db.qdrant import QdrantService
from app.rag.generator import generate_response

logger = logging.getLogger(__name__)


class YouTubeRAGService:
    """
    Service coordinating YouTube transcript ingestion, chunking, embedding, vector storage, and RAG search.
    """

    def __init__(self):
        self.embedder = EmbeddingService()
        self.qdrant = QdrantService()

    def ingest_youtube_video(self, url_or_id: str, target_duration_sec: float = 45.0) -> Dict[str, Any]:
        """
        Ingests a YouTube video transcript into Qdrant.

        Steps:
        1. Extract video ID & fetch captions.
        2. Chunk captions into 45-second time windows.
        3. Embed text chunks using OpenAI text-embedding-3-small.
        4. Upsert chunks into Qdrant collection with video_id metadata.
        """
        video_id = extract_youtube_video_id(url_or_id)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL or Video ID: '{url_or_id}'")

        # 1. Fetch Transcript Cues
        transcript_data = fetch_youtube_transcript(video_id)
        cues = transcript_data["cues"]

        if not cues:
            return {
                "status": "warning",
                "message": f"No text cues found in transcript for video '{video_id}'",
                "video_id": video_id,
                "total_chunks": 0
            }

        # Format cues for chunker with default source_file name
        for c in cues:
            c["source_file"] = f"youtube_{video_id}"
            c["module_name"] = "YouTube Video"
            c["lesson_name"] = f"Video: {video_id}"

        # 2. Time-windowed Chunking
        chunks = create_subtitle_chunks(
            cues,
            target_duration_sec=target_duration_sec,
            overlap_duration_sec=10.0
        )

        if not chunks:
            return {
                "status": "warning",
                "message": "Cues parsed but 0 chunks produced.",
                "video_id": video_id,
                "total_chunks": 0
            }

        # Add video_id to payload
        for chunk in chunks:
            chunk["video_id"] = video_id

        # 3. Generate Embeddings
        chunk_texts = [c["text"] for c in chunks]
        embeddings = self.embedder.embed_documents(chunk_texts)

        # 4. Upsert into Qdrant
        upserted_count = self.qdrant.upsert_chunks(chunks, embeddings)

        return {
            "status": "success",
            "video_id": video_id,
            "total_cues": len(cues),
            "total_chunks": len(chunks),
            "upserted_vectors": upserted_count,
            "sample_chunk": chunks[0] if chunks else None
        }

    def chat_with_youtube_video(self, video_id_or_url: str, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Executes a RAG query scoped to a specific YouTube video.
        Auto-ingests the video transcript into Qdrant if not already indexed.

        Steps:
        1. Extract video ID.
        2. Embed user query string.
        3. Search Qdrant for matching chunks scoped by video_id.
        4. If 0 chunks found for video_id, auto-ingest transcript first.
        5. Synthesize answer with 1-click timestamp citations via LLM.
        """
        video_id = extract_youtube_video_id(video_id_or_url)
        if not video_id:
            video_id = video_id_or_url.strip()

        # 1. Embed query
        query_vector = self.embedder.embed_text(query)

        # 2. Vector Search (over-sample to filter by video_id)
        raw_results = self.qdrant.search(query_vector=query_vector, limit=limit * 10)
        matched_chunks = [r for r in raw_results if r.get("video_id") == video_id]

        # 3. Auto-ingest if not previously indexed in Qdrant
        if not matched_chunks:
            logger.info(f"Video '{video_id}' not yet indexed in Qdrant. Auto-ingesting transcript...")
            ingest_result = self.ingest_youtube_video(video_id)
            if ingest_result.get("status") == "success" and ingest_result.get("total_chunks", 0) > 0:
                # Re-search after successful ingestion
                raw_results = self.qdrant.search(query_vector=query_vector, limit=limit * 10)
                matched_chunks = [r for r in raw_results if r.get("video_id") == video_id]

        # Limit to top-K matches
        context_chunks = matched_chunks[:limit] if matched_chunks else raw_results[:limit]

        # 4. Generate RAG Response
        result = generate_response(prompt=query, context=context_chunks)
        result["video_id"] = video_id
        result["query"] = query
        result["retrieved_chunks_count"] = len(context_chunks)

        return result

