import sys
import time
from pathlib import Path
from app.api.ingest import ingest_path


def main():
    dataset_dir = Path("upload/class-subtitle")
    target_path = sys.argv[1] if len(sys.argv) > 1 else str(dataset_dir)
    
    print(f"=== Subtitle RAG Dataset Ingestion ===")
    print(f"Target Dataset Path: {target_path}")
    
    start_time = time.time()
    result = ingest_path(target_path)
    elapsed = time.time() - start_time
    
    print("\n--- Ingestion Result ---")
    print(f"Status: {result.get('status')}")
    print(f"Message: {result.get('message', 'N/A')}")
    print(f"Processed Files: {result.get('processed_files')}")
    print(f"Total Subtitle Chunks: {result.get('total_chunks')}")
    print(f"Upserted Vectors: {result.get('upserted_vectors')}")
    print(f"Time Taken: {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()
