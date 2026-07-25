# YouTube Video AI Co-Pilot — System Design & Architecture

> **Goal**: Enable instant, sub-second natural language question answering over any 2-hour+ YouTube video or playlist with 1-click video timestamp seeking.

---

## 1. Architecture Overview

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                         1. TRANSCRIPT FETCH                            │
 │                                                                        │
 │   User pastes YouTube URL:  https://youtube.com/watch?v=VIDEO_ID       │
 │   Fetch captions via `youtube-transcript-api` (< 1.5 seconds)          │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                    2. TIME-WINDOWED CHUNKING (45s)                     │
 │                                                                        │
 │   Group raw cues into 45-second windows with 10s overlap:             │
 │   - text: "In this section we handle form validation..."               │
 │   - start_sec: 4462.5  --> start_time_str: "01:14:22"                 │
 │   - end_sec: 4507.5    --> end_time_str: "01:15:07"                   │
 │   - video_id: "VIDEO_ID"                                               │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                     3. EMBEDDING & QDRANT STORAGE                      │
 │                                                                        │
 │   - Embed text with OpenAI `text-embedding-3-small` (1536 dims).        │
 │   - Store points in Qdrant with `video_id` payload index.             │
 │   - Caching: If `video_id` already exists in Qdrant, skip ingestion.   │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                   4. RAG RETRIEVAL & GENERATION                        │
 │                                                                        │
 │   Query: "How do we validate forms?"                                   │
 │   Vector Search -> Top-5 matching 45s chunks for `video_id`.           │
 │   LLM generates answer with inline timestamp badges: `[01:14:22]`.      │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                    5. FRONTEND CLICK-TO-SEEK                           │
 │                                                                        │
 │   Clicking badge `[01:14:22]` in UI executes:                          │
 │   `player.seekTo(4462)` on YouTube Embedded iFrame.                    │
 └────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Why Time-Windowed RAG for YouTube Videos?

A 2-hour YouTube video contains ~15,000–18,000 spoken words (~20,000–25,000 tokens).

- **Direct Prompt Injection (No RAG)**: Sending 25,000 tokens per message is slow (5–10s latency), expensive, and fails for multi-video playlists.
- **Time-Windowed RAG (Selected Solution)**: Chunking into 45-second time windows enables **sub-second retrieval**, **95% lower cost**, and **exact timestamp pinpointing (`01:14:22`)**.

---

## 3. Data Schema

### Qdrant Point Structure
```json
{
  "id": "uuid-v4",
  "vector": [0.012, -0.045, "... 1536 float values ..."],
  "payload": {
    "video_id": "bMknfKXIFA8",
    "text": "In this section we talk about state management and props...",
    "start_sec": 4462.5,
    "end_sec": 4507.5,
    "start_time_str": "01:14:22",
    "end_time_str": "01:15:07",
    "timestamp_range": "01:14:22 - 01:15:07"
  }
}
```

---

## 4. Performance & Latency Budget (2-Hour Video)

1. **Transcript Fetch**: ~1.2s (one-time API fetch)
2. **Time-Windowed Chunking (~160 chunks)**: < 0.05s
3. **OpenAI Embedding (Batch 160 chunks in 1 request)**: ~0.8s
4. **Qdrant Vector Storage**: ~0.2s
5. **Total Ingestion Time**: **~2.2 seconds total (cached in DB afterwards)**
6. **Chat Query Latency**: **~0.8 to 1.5 seconds**

---

## 5. API Endpoints Plan

### `POST /api/yt/ingest`
- **Request**: `{ "url_or_id": "https://www.youtube.com/watch?v=XXXXX" }`
- **Response**: `{ "status": "success", "video_id": "XXXXX", "chunks_count": 160, "already_cached": false }`

### `POST /api/yt/chat`
- **Request**: `{ "video_id": "XXXXX", "query": "How do we handle form validation?", "limit": 5 }`
- **Response**: `{ "answer": "...", "sources": [{ "timestamp_range": "01:14:22 - 01:15:07", "start_sec": 4462.5, "text": "..." }] }`
