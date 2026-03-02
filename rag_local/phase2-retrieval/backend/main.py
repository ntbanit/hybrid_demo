from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from retriever import hybrid_search

app = FastAPI(title="RAG Retrieval API")

app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"], allow_headers=["*"])

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/search")
def search(req: SearchRequest):
    results = hybrid_search(req.query, req.top_k)
    return {"query": req.query, "results": results}

@app.get("/health")
def health():
    return {"status": "ok"}