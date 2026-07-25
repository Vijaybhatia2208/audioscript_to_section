import os
import hashlib
import logging
from typing import List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from openai import OpenAI
except ImportError:
    openai = None
    OpenAI = None

logger = logging.getLogger(__name__)



class EmbeddingService:
    """
    Embedding service generating vector representations for text chunks.
    Uses OpenAI's text-embedding API (default: text-embedding-3-small).
    Falls back to deterministic hashing if no OpenAI API key is configured.
    """

    def __init__(self, model_name: str = "text-embedding-3-small", api_key: Optional[str] = None):
        """
        Initialize OpenAI Embedding Service.

        Args:
            model_name (str): OpenAI embedding model name. Defaults to 'text-embedding-3-small'.
            api_key (Optional[str]): OpenAI API Key. Defaults to OPENAI_API_KEY environment variable.
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.dimension = 1536  # Standard vector dimension for text-embedding-3-small / text-embedding-ada-002
        self.client = None

        if OpenAI and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}. Falling back to offline mode.")
        elif not self.api_key:
            logger.info("OPENAI_API_KEY environment variable not set. Using offline deterministic hashing fallback.")

    def embed_text(self, text: str) -> List[float]:
        """
        Generates a vector embedding for a single text input using OpenAI.

        Args:
            text (str): Input text string.

        Returns:
            List[float]: Vector embedding.
        """
        if self.client:
            try:
                response = self.client.embeddings.create(
                    input=[text],
                    model=self.model_name
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"OpenAI API call failed: {e}. Using offline fallback.")

        return self._hash_fallback(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generates vector embeddings for a list of document texts using OpenAI embeddings.
        Batches requests for efficient network throughput.

        Args:
            texts (List[str]): List of input text strings.

        Returns:
            List[List[float]]: List of vector embeddings corresponding to inputs.
        """
        if not texts:
            return []

        if self.client:
            try:
                # Batch in groups of 100 for optimal API request performance
                batch_size = 100
                all_embeddings = []
                for i in range(0, len(texts), batch_size):
                    batch = texts[i : i + batch_size]
                    response = self.client.embeddings.create(
                        input=batch,
                        model=self.model_name
                    )
                    batch_embeddings = [data.embedding for data in response.data]
                    all_embeddings.extend(batch_embeddings)
                return all_embeddings
            except Exception as e:
                logger.error(f"OpenAI API call failed: {e}. Using offline fallback.")

        return [self._hash_fallback(t) for t in texts]

    def _hash_fallback(self, text: str) -> List[float]:
        """
        Deterministic offline vector generator for local testing when API key is missing.
        """
        hash_digest = hashlib.sha256(text.encode("utf-8")).digest()
        vector = []
        for i in range(self.dimension):
            byte_val = hash_digest[i % len(hash_digest)]
            val = (byte_val / 255.0) * 2.0 - 1.0
            vector.append(val)
        return vector

