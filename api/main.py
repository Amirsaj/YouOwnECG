"""
YouOwnECG FastAPI application.

Start with: uvicorn api.main:app --reload --port 8000

Environment variables:
  DEEPSEEK_API_KEY    — DeepSeek API key (required for agent calls)
  DEEPSEEK_BASE_URL   — API base URL (default: https://api.deepseek.com/v1)
  DEEPSEEK_MODEL      — Model ID (default: deepseek-reasoner)
  DB_PATH             — SQLite path (default: data/youownecg.db)
  OPENAI_API_KEY      — OpenAI API key (required for RAG embeddings)
  RAG_INDEX_PATH      — FAISS index path (default: data/rag/faiss.index)
  RAG_META_PATH       — Chunk metadata path (default: data/rag/chunks_meta.json)
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.ecg import router as ecg_router
from api.routes.qa import router as qa_router

RAG_INDEX_PATH = os.environ.get("RAG_INDEX_PATH", "data/rag/faiss.index")
RAG_META_PATH = os.environ.get("RAG_META_PATH", "data/rag/chunks_meta.json")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the RAG store once at startup; release on shutdown."""
    from pathlib import Path
    if Path(RAG_INDEX_PATH).exists() and Path(RAG_META_PATH).exists():
        from rag.embedding import EmbeddingStore
        app.state.rag_store = EmbeddingStore.load(RAG_INDEX_PATH, RAG_META_PATH)
        print(f"RAG store loaded: {app.state.rag_store._index.ntotal} vectors")
    else:
        app.state.rag_store = None
        print("RAG store not found — agents will run without textbook evidence")
    yield
    app.state.rag_store = None


app = FastAPI(
    title="YouOwnECG",
    description="AI-assisted 12-lead ECG analysis for ER clinicians.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3003", "http://localhost:3004"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ecg_router)
app.include_router(qa_router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
