import os
import logging
from typing import List, Dict, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)


# System prompt forcing grounded answers with exact course subtitle citations
SYSTEM_PROMPT = """You are an expert AI teaching assistant for an online video course.
Your job is to answer student questions based ONLY on the provided course subtitle context chunks.

STRICT RULES:
1. Answer the student's question accurately and concisely using ONLY the information provided in the Context Chunks.
2. For EVERY key point or answer detail, explicitly cite the source lesson and timestamp range using this exact format:
   [Module: <module_name> | Lesson: <lesson_name> | Time: <timestamp_range>]
3. If the answer cannot be found in the provided context, politely inform the student that the information is not covered in the current course subtitles. Do NOT invent or hallucinate information outside the context.
4. Keep your tone encouraging, professional, and clear.
"""


class RAGGenerator:
    """
    RAG Generator class using OpenAI chat models to generate grounded answers with subtitle citations.
    """

    def __init__(self, model_name: str = "gpt-4o-mini", api_key: Optional[str] = None):
        """
        Initialize the RAG generator client.

        Args:
            model_name (str): OpenAI chat model name. Defaults to "gpt-4o-mini".
            api_key (Optional[str]): OpenAI API Key. Defaults to OPENAI_API_KEY environment variable.
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None

        if OpenAI and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client for generator: {e}")
        elif not self.api_key:
            logger.info("OPENAI_API_KEY not set. RAGGenerator running in fallback mode.")

    def format_context(self, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Formats Qdrant search result chunks into structured text block for the LLM prompt.

        Args:
            context_chunks (List[Dict[str, Any]]): Retrieved Qdrant payload items.

        Returns:
            str: Formatted context string.
        """
        if not context_chunks:
            return "No relevant subtitle context found."

        formatted_blocks = []
        for idx, chunk in enumerate(context_chunks, start=1):
            module = chunk.get("module_name", "Unknown Module")
            lesson = chunk.get("lesson_name", "Unknown Lesson")
            time_range = chunk.get("timestamp_range", "00:00 - 00:00")
            text = chunk.get("text", "").strip()

            block = (
                f"--- Context Chunk {idx} ---\n"
                f"Module: {module}\n"
                f"Lesson: {lesson}\n"
                f"Timestamp Range: {time_range}\n"
                f"Subtitle Content:\n\"{text}\""
            )
            formatted_blocks.append(block)

        return "\n\n".join(formatted_blocks)

    def generate(self, prompt: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates a grounded RAG response using OpenAI Chat Completions.

        Args:
            prompt (str): Student's query string.
            context_chunks (List[Dict[str, Any]]): Top-K matching subtitle chunks from Qdrant search.

        Returns:
            Dict[str, Any]: Dictionary containing:
                - "answer" (str): Generated answer text with inline citations.
                - "sources" (List[Dict]): Unique source citation metadata.
                - "model" (str): LLM model used.
        """
        formatted_context = self.format_context(context_chunks)

        user_message_content = (
            f"STUDENT QUESTION:\n{prompt}\n\n"
            f"PROVIDED SUBTITLE CONTEXT CHUNKS:\n"
            f"{formatted_context}\n\n"
            f"Please answer the student's question adhering strictly to the system prompt rules and include citations."
        )

        sources = []
        for c in context_chunks:
            sources.append({
                "module_name": c.get("module_name"),
                "lesson_name": c.get("lesson_name"),
                "timestamp_range": c.get("timestamp_range"),
                "start_time_str": c.get("start_time_str"),
                "end_time_str": c.get("end_time_str"),
                "source_file": c.get("source_file"),
                "score": c.get("score")
            })

        if not self.client:
            # Fallback output if no API key is provided
            return {
                "answer": (
                    f"[Offline Fallback] OpenAI API key is missing. "
                    f"Retrieved {len(context_chunks)} matching context chunk(s) from Qdrant.\n\n"
                    f"Top matching text:\n\"{context_chunks[0]['text']}\"" if context_chunks else "No context available."
                ),
                "sources": sources,
                "model": "offline-fallback"
            }

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message_content}
                ],
                temperature=0.2
            )

            answer_text = response.choices[0].message.content

            return {
                "answer": answer_text,
                "sources": sources,
                "model": self.model_name
            }
        except Exception as e:
            logger.error(f"Error during OpenAI LLM response generation: {e}")
            return {
                "answer": f"Error generating response: {str(e)}",
                "sources": sources,
                "model": self.model_name
            }


def generate_response(prompt: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convenience function interface for RAG generation.

    Args:
        prompt (str): User question string.
        context (List[Dict[str, Any]]): Retrieved Qdrant context chunks.

    Returns:
        Dict[str, Any]: Answer and source citations dictionary.
    """
    generator = RAGGenerator()
    return generator.generate(prompt, context)

