import uuid
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


class QdrantService:
    """
    Service wrapper for managing Qdrant vector database operations.
    
    Handles vector database connection initialization, collection creation,
    batch payload vector upserts(UPDATE , INSERTS), and cosine similarity vector searches for
    subtitle chunks.
    """

    def __init__(self, collection_name: str = "course_subtitles", host: str = "localhost", port: int = 6333):
        """
        Initialize the Qdrant service client.

        Args:
            collection_name (str): Name of the Qdrant vector collection to target. Defaults to "course_subtitles".
            host (str): Qdrant server host address. Defaults to "localhost".
            port (int): Qdrant server REST API port. Defaults to 6333.
        """
        self.collection_name = collection_name
        self.host = host
        self.port = port
        self.client = None

        # Attempt connection to a live Qdrant Docker container on host:port.
        # Fall back gracefully to an in-memory client for local offline testing if container connection fails.
        try:
            self.client = QdrantClient(host=self.host, port=self.port, timeout=2.0)
            # Ping/fetch collections to verify active network connection
            self.client.get_collections()
        except Exception:
            # Docker instance not running or unreachable -> use fast in-memory engine
            self.client = QdrantClient(":memory:")

    def create_collection_if_not_exists(self, vector_size: int = 384):
        """
        Ensures that the target Qdrant collection exists before insertion or query.

        Args:
            vector_size (int): Dimension of the embedding vectors (e.g., 384 for all-MiniLM-L6-v2).
        """
        # Retrieve names of all currently existing collections in Qdrant instance
        collections = [c.name for c in self.client.get_collections().collections]

        # Create a new collection configured with Cosine distance metric if missing
        if self.collection_name not in collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )

    def upsert_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> int:
        """
        Upserts subtitle text chunks along with their vector embeddings and metadata payload into Qdrant.

        Args:
            chunks (List[Dict[str, Any]]): List of subtitle chunk dictionaries containing metadata.
            embeddings (List[List[float]]): Corresponding dense vector embeddings for each chunk.

        Returns:
            int: The total count of points successfully prepared and upserted into Qdrant.
        """
        # Early return if there are no chunks or embeddings to process
        if not chunks or not embeddings:
            return 0

        # Dynamically detect vector dimension size from the first embedding vector
        vector_dim = len(embeddings[0])
        self.create_collection_if_not_exists(vector_size=vector_dim)

        points = []
        # Pair each subtitle chunk with its corresponding embedding vector
        for chunk, embedding in zip(chunks, embeddings):
            # Generate a unique string UUID for each point entry
            point_id = str(uuid.uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    # Store rich subtitle metadata in payload for downstream retrieval and answer grounding
                    payload={
                        "text": chunk["text"],
                        "module_name": chunk["module_name"],
                        "lesson_name": chunk["lesson_name"],
                        "start_time_str": chunk["start_time_str"],
                        "end_time_str": chunk["end_time_str"],
                        "timestamp_range": chunk["timestamp_range"],
                        "start_sec": chunk["start_sec"],
                        "end_sec": chunk["end_sec"],
                        "source_file": chunk["source_file"]
                    }
                )
            )

        # Execute chunked batch upserts to respect Qdrant HTTP request size limits (32 MB)
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch_points = points[i : i + batch_size]
            self.client.upsert(collection_name=self.collection_name, points=batch_points)

        return len(points)


    def search(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Searches the Qdrant collection for chunks vector-similar to the given query vector.

        Args:
            query_vector (List[float]): Embedded vector representation of the user query.
            limit (int): Maximum number of top matching results to retrieve. Defaults to 5.

        Returns:
            List[Dict[str, Any]]: List of dictionary payloads corresponding to top matches,
                                  with similarity 'score' attached.
        """
        # Execute nearest neighbor search using modern query_points API or search fallback
        if hasattr(self.client, "query_points"):
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit
            )
            results = response.points
        else:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )

        output = []
        # Convert Qdrant ScoredPoint search result items into standard dict structures with scores
        for res in results:
            item = dict(res.payload) if res.payload else {}
            item["score"] = res.score
            output.append(item)
        return output


