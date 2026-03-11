import sys
import os
import re
import json
import numpy as np
from openai import OpenAI

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils import read_techcorp_docs, get_doc_info
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

# ─── Configuration ────────────────────────────────────────────────────────────
API_KEY    = os.environ.get("GEMINI_API_KEY")
API_BASE   = os.environ.get("GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta/openai/")
MODEL_NAME = "gemini-2.5-flash-lite"
print(f"🔌 API KEY: {API_KEY}")
print(f"🔌 API Endpoint: {API_BASE}")
print(f"🧠 Model: {MODEL_NAME}")
print()
client = OpenAI(api_key=API_KEY, base_url=API_BASE)

# ─── Load documents ───────────────────────────────────────────────────────────
docs, doc_paths = read_techcorp_docs()

# ─── Pre-build indexes (done once) ────────────────────────────────────────────
# Vector index
_embed_model   = SentenceTransformer('all-MiniLM-L6-v2')
_doc_embeddings = _embed_model.encode(docs)

# BM25 index
_tokenized_docs = [re.sub(r'[^a-zA-Z\s]', '', d.lower()).split() for d in docs]
_bm25           = BM25Okapi(_tokenized_docs)

TOP_K = 10   # candidates per retriever before fusion
FINAL_K = 3  # results returned after reranking


# ─── Step 1 · Keyword Search (BM25) ───────────────────────────────────────────
def keyword_search(query: str, top_k: int = TOP_K) -> list[dict]:
    """Return ranked list of {idx, score, doc, path} using BM25."""
    tokenized_query = re.sub(r'[^a-zA-Z\s]', '', query.lower()).split()
    scores = _bm25.get_scores(tokenized_query)
    top_indices = scores.argsort()[-top_k:][::-1]
    return [
        {"idx": int(i), "score": float(scores[i]), "doc": docs[i], "path": doc_paths[i]}
        for i in top_indices
    ]


# ─── Step 2 · Vector Search (Semantic) ────────────────────────────────────────
def vector_search(query: str, top_k: int = TOP_K) -> list[dict]:
    """Return ranked list of {idx, score, doc, path} using cosine similarity."""
    query_embedding = _embed_model.encode([query])
    similarities    = np.dot(query_embedding, _doc_embeddings.T).flatten()
    top_indices     = similarities.argsort()[-top_k:][::-1]
    return [
        {"idx": int(i), "score": float(similarities[i]), "doc": docs[i], "path": doc_paths[i]}
        for i in top_indices
    ]


# ─── Step 3 · RRF Fusion ──────────────────────────────────────────────────────
def rrf(keyword_results: list[dict], vector_results: list[dict],
        k: int = 60, top_k: int = TOP_K) -> list[dict]:
    """
    Reciprocal Rank Fusion.
    Score = Σ 1 / (k + rank)  over both ranked lists.
    """
    rrf_scores: dict[int, float] = {}

    for rank, item in enumerate(keyword_results, start=1):
        rrf_scores[item["idx"]] = rrf_scores.get(item["idx"], 0.0) + 1.0 / (k + rank)

    for rank, item in enumerate(vector_results, start=1):
        rrf_scores[item["idx"]] = rrf_scores.get(item["idx"], 0.0) + 1.0 / (k + rank)

    sorted_indices = sorted(rrf_scores, key=rrf_scores.get, reverse=True)[:top_k]
    return [
        {"idx": idx, "score": rrf_scores[idx], "doc": docs[idx], "path": doc_paths[idx]}
        for idx in sorted_indices
    ]


# ─── Step 4 · Reranking (Gemini) ──────────────────────────────────────────────
def reranking(query: str, candidates: list[dict], final_k: int = FINAL_K) -> list[dict]:
    """
    Ask Gemini to rerank the RRF candidates and return the top-final_k results
    with a short relevance explanation.
    """
    numbered_docs = "\n\n".join(
        f"[{i+1}] ({os.path.basename(item['path'])})\n{item['doc'][:400]}"
        for i, item in enumerate(candidates)
    )

    prompt = (
        f"You are a precise document reranker.\n\n"
        f"Query: {query}\n\n"
        f"Below are {len(candidates)} candidate documents (truncated).\n"
        f"Rerank them from most to least relevant to the query.\n"
        f"Reply ONLY with a JSON array – no markdown fences, no extra text:\n"
        f'[{{"rank": 1, "doc_number": <1-based int>, "reason": "<one sentence>"}}, ...]\n\n'
        f"Documents:\n{numbered_docs}"
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.choices[0].message.content.strip()

    try:
        raw_clean = re.sub(r"```[a-z]*\n?|```", "", raw).strip()
        ranking   = json.loads(raw_clean)
    except json.JSONDecodeError:
        print("  ⚠️  Reranker parse error – returning RRF order.")
        print(f"  Raw response: {raw[:200]}")
        return candidates[:final_k]

    reranked = []
    for entry in ranking[:final_k]:
        doc_idx = entry["doc_number"] - 1   # convert to 0-based
        if 0 <= doc_idx < len(candidates):
            item = candidates[doc_idx].copy()
            item["rerank_reason"] = entry.get("reason", "")
            reranked.append(item)
    return reranked


# ─── Full Hybrid Pipeline ─────────────────────────────────────────────────────
def hybrid_search(query: str) -> list[dict]:
    print(f"\n🔎 Query: '{query}'")
    print("=" * 60)

    # 1 – Keyword
    kw_results = keyword_search(query)
    for i in range(len(kw_results)):
        print(f"1️⃣  Keyword  – top doc: {os.path.basename(kw_results[i]['path'])}  "
            f"(score {kw_results[i]['score']:.4f})")

    # 2 – Vector
    vec_results = vector_search(query)
    for i in range(len(vec_results)):
        print(f"2️⃣  Vector   – top doc: {os.path.basename(vec_results[i]['path'])}  "
            f"(score {vec_results[i]['score']:.4f})")

    # 3 – RRF
    fused = rrf(kw_results, vec_results)
    for i in range(len(fused)):
        print(f"3️⃣  RRF      – top doc: {os.path.basename(fused[i]['path'])}  "
            f"(score {fused[i]['score']:.4f})")

    # 4 – Reranking
    final = reranking(query, fused, final_k=5)
    print(f"4️⃣  Reranking – Gemini selected {len(final)} best results:\n")

    for i, item in enumerate(final, 1):
        doc_name = os.path.basename(item['path'])
        reason   = item.get('rerank_reason', '')
        print(f"  {i}. {doc_name}")
        if reason:
            print(f"     └─ {reason}")

    return final


# ─── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    query = "What is the phone 1-800-832-4267 using for?"
    results = hybrid_search(query)