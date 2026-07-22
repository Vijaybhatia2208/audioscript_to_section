# Advanced RAG System Implementation Plan: Next.js Full-Stack Udemy Course Assistant

Implement a unified full-stack **Next.js (App Router + TypeScript)** application for searching and answering student questions across Udemy course subtitle files (`.srt` and `.vtt` format) located in `class-subtitle`. Both frontend and backend API endpoints/server logic will reside within the single Next.js project.

The system returns answers enriched with exact **Module Name**, **Lesson Name**, and **Timestamps** (`HH:MM:SS`). Additionally, provide a complete **Multimodal System Design** for scaling to video keyframes, OCR slides, and audio.

---

## Technical Stack & Architecture Choice

- **Framework**: Next.js (App Router, TypeScript, React)
- **Project Location**: `file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag`
- **Backend Logic**: Next.js API Routes (`app/api/ingest/route.ts`, `app/api/query/route.ts`) & Server Modules (`lib/rag/*`, `lib/ingestion/*`).
- **Vector DB**: In-Memory Vector Store / Qdrant with payload metadata filtering (`module_name`, `lesson_name`, `start_time_seconds`, `end_time_seconds`, `timestamp_str`, `source_file`).
- **LLM & Embeddings**: Google Gemini API (`@google/genai` / `gemini-2.5-flash`, `text-embedding-004`) or OpenAI models via clean adapter pattern.
- **Frontend UI**: Simple clean Next.js interactive interface (`app/page.tsx`) with execution trace visualization and timestamp badges.

---

## System Architecture Diagram

```
                             ┌───────────────────────────────┐
                             │    Next.js Client (React)     │
                             └───────────────┬───────────────┘
                                             │ HTTP / API Call
                             ┌───────────────▼───────────────┐
                             │   app/api/query/route.ts      │
                             └───────────────┬───────────────┘
                                             │
                             ┌───────────────▼───────────────┐
                             │      Input Guardrails         │
                             │    (PII / Safety / Scope)     │
                             └───────────────┬───────────────┘
                                             │
                             ┌───────────────▼───────────────┐
                             │      Query Translation &      │
                             │         Decomposition         │
                             │    • Step-Back Prompting      │
                             │    • Sub-Query Breakdown      │
                             │    • HyDE Vector Query        │
                             └───────────────┬───────────────┘
                                             │
                             ┌───────────────▼───────────────┐
                             │    Intent Router & Adapters   │
                             │    (Vector DB / SQL / Meta)   │
                             └───────────────┬───────────────┘
                                             │
                             ┌───────────────▼───────────────┐
                             │     Multi-Query Vector        │
                             │      Search + RRF Rank        │
                             └───────────────┬───────────────┘
                                             │
                             ┌───────────────▼───────────────┐
                             │      CRAG Evaluator Loop      │
                             │  (Relevance Check / Rewrite)  │
                             └───────────────┬───────────────┘
                                             │
                             ┌───────────────▼───────────────┐
                             │      Answer Synthesizer       │
                             │     + Timestamp Citation      │
                             └───────────────┬───────────────┘
                                             │
                             ┌───────────────▼───────────────┐
                             │      Output Guardrails        │
                             │      (Grounding Verify)       │
                             └───────────────────────────────┘
```

---

## User Review Required

> [!IMPORTANT]
> **Single Unified Full-Stack App**: Next.js App Router allows API routes and UI components in a single repository. Subtitle files will be ingested from `class-subtitle` via an administrative API route (`/api/ingest`) or CLI script (`scripts/ingest.ts`).

---

## Sequential 13-Step Next.js Execution Plan

### Step 1: Next.js Project Creation & Configuration

- Initialize Next.js project with TypeScript and App Router support in `course_subtitles_rag`.
- Install dependencies: `@google/genai`, `dotenv`, `@types/node`.
- Configure `.env.local` for API keys and environment variables.

#### [NEW] [package.json](file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag/package.json)

#### [NEW] [tsconfig.json](file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag/tsconfig.json)

#### [NEW] [.env.local.example](file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag/.env.local.example)

---

### Step 2: SRT & VTT Subtitle File Parser

- Implement `lib/ingestion/srt-vtt-parser.ts` to recursively scan `class-subtitle/module X/...`.
- Parse SRT and VTT timecodes into standardized seconds and timestamp strings (`HH:MM:SS`).
- Extract Module Name and Lesson Name.

#### [NEW] [srt-vtt-parser.ts](file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag/lib/ingestion/srt-vtt-parser.ts)

---

### Step 3: Time-Aware Semantic Subtitle Chunker

- Implement `lib/ingestion/chunker.ts`.
- Apply sliding window chunking (~60s window with 15s overlap) over subtitle cues.
- Track `start_timestamp` and `end_timestamp` of each chunk and format text payload with contextual header metadata.

#### [NEW] [chunker.ts](file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag/lib/ingestion/chunker.ts)

---

### Step 4: Vector Store Schema & Ingestion Script

- Implement `lib/ingestion/vector-store.ts` supporting HNSW in-memory vector database or Qdrant.
- Store metadata: `{ text, module_name, lesson_name, start_time_sec, end_time_sec, timestamp_str, source_file }`.
- Provide indexing script `scripts/ingest.ts` and API route `/api/ingest/route.ts`.

#### [NEW] [vector-store.ts](file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag/lib/ingestion/vector-store.ts)

#### [NEW] [route.ts (ingest)](file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag/app/api/ingest/route.ts)

#### [NEW] [ingest.ts](file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag/scripts/ingest.ts)

---

### Step 5: Input & Output Guardrails Layer

- Implement `lib/rag/guardrails.ts`.
- Input Guardrails: Safety, PII check, out-of-scope validation.
- Output Guardrails: Answer grounding and timestamp accuracy validation.

#### [NEW] [guardrails.ts](file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag/lib/rag/guardrails.ts)

---

### Step 6: Query Translation Engine (Step-Back, Sub-Queries & HyDE)

- Implement `lib/rag/query-translator.ts`.
- Step-Back Abstraction generator.
- Sub-Query Decomposition generator.
- HyDE (Hypothetical Document Embedding) generator.

#### [NEW] [query-translator.ts](file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag/lib/rag/query-translator.ts)

---

### Step 7: Intent Router & Vector Retriever

- Implement `lib/rag/router.ts` & `lib/rag/retriever.ts`.
- Route intent (Meta information vs Content search).
- Vector retrieval across all query variants.

#### [NEW] [router.ts](file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag/lib/rag/router.ts)

#### [NEW] [retriever.ts](file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag/lib/rag/retriever.ts)

---

### Step 8: Reciprocal Rank Fusion (RRF) Reranker

- Implement `lib/rag/rrf-ranker.ts`.
- Reciprocal Rank Fusion scoring:
  $$RRF\_Score(d) = \sum_{q \in Q} \frac{1}{k + rank(q, d)}$$
- Deduplicate and rank Top 5 context chunks.

#### [NEW] [rrf-ranker.ts](file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag/lib/rag/rrf-ranker.ts)

---

### Step 9: Corrective RAG (CRAG) Evaluator

- Implement `lib/rag/crag-evaluator.ts`.
- Evaluator model checks document relevance (`Correct`, `Ambiguous`, `Incorrect`).
- Triggers Query Rewrite loop if relevance is low.

#### [NEW] [crag-evaluator.ts](file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag/lib/rag/crag-evaluator.ts)

---

### Step 10: Answer Synthesizer with Lesson & Timestamp Citations

- Implement `lib/rag/generator.ts`.
- Synthesizes student response with exact formatted markdown citations:
  > **Lesson**: `01_what-is-mobile-development_epm` (Module 1)  
  > **Timestamp**: `00:00:04 - 00:00:36`

#### [NEW] [generator.ts](file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag/lib/rag/generator.ts)

---

### Step 11: Next.js Full-Stack API Route & UI Interface

- Implement Next.js API Route `app/api/query/route.ts` orchestrating the RAG pipeline and returning answer + execution trace.
- Implement simple React UI `app/page.tsx` with search bar, response card, clickable timestamp badges, and live trace visualization.

#### [NEW] [route.ts (query)](file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag/app/api/query/route.ts)

#### [NEW] [page.tsx](file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag/app/page.tsx)

---

### Step 12: Multimodal Architecture Specification (Images & Video Scaling)

- Create `docs/multimodal_system_design.md` detailing architecture to scale from Subtitles -> Slide Frames (OCR/Vision) -> Full Video (`ffmpeg` keyframes + Whisper audio + unified temporal index).

#### [NEW] [multimodal_system_design.md](file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag/docs/multimodal_system_design.md)

---

### Step 13: Automated Testing & RAG Evaluation Suite

- Implement test suite `scripts/test-rag.ts` to run automated verification queries against the Next.js API endpoint.

#### [NEW] [test-rag.ts](file:///Users/littlegiant/Documents/ai_ml_cohort/course_subtitles_rag/scripts/test-rag.ts)

---

## Verification Plan

### Automated Tests

- Run `npx tsx scripts/ingest.ts` to verify subtitle parsing and vector store population.
- Run `npx tsx scripts/test-rag.ts` to verify Next.js RAG pipeline response structure and timestamp accuracy.

### Manual Verification

- Run `npm run dev` and open `http://localhost:3000`.
- Ask course questions (e.g. _"What is mobile development?"_) and verify that exact lesson name and timestamps are displayed on screen.
