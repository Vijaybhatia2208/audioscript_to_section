import sys
import json
from app.embeddings.embedding_service import EmbeddingService
from app.vector_db.qdrant import QdrantService
from app.rag.generator import generate_response


def main():
    default_query = "What is mobile development?"
    query = sys.argv[1] if len(sys.argv) > 1 else default_query

    print(f"=== Course Subtitle RAG Search & Query ===")
    print(f"Query: \"{query}\"\n")

    # 1. Embed query
    embedder = EmbeddingService()
    query_vector = embedder.embed_text(query)

    # 2. Search Qdrant
    qdrant = QdrantService()
    chunks = qdrant.search(query_vector, limit=5)
    print(f"Retrieved {len(chunks)} matching chunk(s) from Qdrant.\n")

    # 3. Generate answer
    response = generate_response(query, chunks)

    print("=== RAG Answer ===")
    print(response.get("answer"))

    print("\n=== Citation Sources ===")
    for idx, src in enumerate(response.get("sources", []), start=1):
        print(f"  {idx}. Module: {src.get('module_name')} | Lesson: {src.get('lesson_name')} | Time: {src.get('timestamp_range')} | Score: {src.get('score', 0):.4f}")


if __name__ == "__main__":
    main()
