from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.embeddings.embedding_service import EmbeddingService
from app.vector_db.qdrant import QdrantService
from app.rag.generator import generate_response

router = APIRouter()


class QueryRequest(BaseModel):
    query: str = Field(..., description="Student query or search question string", example="What is mobile development?")
    limit: Optional[int] = Field(default=5, description="Number of top context chunks to retrieve from Qdrant", ge=1, le=20)


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[Dict[str, Any]]
    retrieved_chunks_count: int
    model: str


@router.post("/chat", response_model=QueryResponse)
@router.post("/query", response_model=QueryResponse)
async def query_subtitles(request: QueryRequest):
    """
    Search & Question Answering Endpoint for Course Subtitles.

    1. Embeds student search query string using OpenAI embedding model.
    2. Searches Qdrant vector database for top matching subtitle chunks.
    3. Runs RAG response generator to synthesize an answer with citations.
    """
    query_text = request.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    try:
        # 1. Embed student query
        embedder = EmbeddingService()
        query_vector = embedder.embed_text(query_text)

        # 2. Search Qdrant vector collection
        qdrant = QdrantService()
        context_chunks = qdrant.search(query_vector=query_vector, limit=request.limit)

        # 3. Generate grounded RAG answer
        result = generate_response(prompt=query_text, context=context_chunks)

        return QueryResponse(
            query=query_text,
            answer=result.get("answer", ""),
            sources=result.get("sources", []),
            retrieved_chunks_count=len(context_chunks),
            model=result.get("model", "unknown")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

