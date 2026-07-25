import sys
import json
from app.yt.yt_service import YouTubeRAGService


def main():
    default_url = "https://www.youtube.com/watch?v=bMknfKXIFA8"  # React in 100 seconds
    default_query = "What is state and how does it work?"

    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    query = sys.argv[2] if len(sys.argv) > 2 else default_query

    print("=== YouTube Video AI Co-Pilot Test ===")
    print(f"Target Video URL: {url}")
    print(f"Query: \"{query}\"\n")

    service = YouTubeRAGService()

    # 1. Ingest YouTube Video
    print("Fetching transcript & ingesting into Qdrant...")
    ingest_res = service.ingest_youtube_video(url)
    print(f"Status: {ingest_res.get('status')}")
    print(f"Video ID: {ingest_res.get('video_id')}")
    print(f"Total Cues: {ingest_res.get('total_cues')}")
    print(f"Total 45s Chunks: {ingest_res.get('total_chunks')}")
    print(f"Upserted Vectors: {ingest_res.get('upserted_vectors')}\n")

    # 2. Chat Query
    print(f"Running RAG Query...")
    chat_res = service.chat_with_youtube_video(url, query)

    print("\n=== AI Answer ===")
    print(chat_res.get("answer"))

    print("\n=== Timestamp Citations ===")
    for idx, src in enumerate(chat_res.get("sources", []), start=1):
        print(f"  {idx}. Time: {src.get('timestamp_range')} (start_sec: {src.get('start_sec')}) | Score: {src.get('score', 0):.4f}")


if __name__ == "__main__":
    main()
