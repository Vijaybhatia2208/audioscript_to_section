import json
import sys
from pathlib import Path
from app.api.ingest import ingest_path


def main():
    # Default target file for testing
    default_file = Path("upload/class-subtitle/module 1/01_what-is-mobile-development_epm/01_what-is-mobile-development_epm.srt")
    
    target_path = sys.argv[1] if len(sys.argv) > 1 else str(default_file)
    print(f"=== Testing Local Subtitle Ingestion ===")
    print(f"Target Path: {target_path}")
    
    result = ingest_path(target_path)
    
    print("\n--- Ingestion Result ---")
    print(f"Status: {result.get('status')}")
    print(f"Processed Files: {result.get('processed_files')}")
    print(f"Total Chunks: {result.get('total_chunks')}")
    print(f"Upserted Vectors: {result.get('upserted_vectors')}")
    
    if result.get("sample_chunk"):
        print("\n--- Sample Ingested Chunk ---")
        print(json.dumps(result["sample_chunk"], indent=2))


if __name__ == "__main__":
    main()
