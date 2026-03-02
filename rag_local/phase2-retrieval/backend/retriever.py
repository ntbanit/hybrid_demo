
from sentence_transformers import SentenceTransformer
import psycopg2, weaviate
from elasticsearch import Elasticsearch

MODEL = SentenceTransformer("all-MiniLM-L6-v2")
PG    = "postgresql://rag:ragpass@localhost:5432/ragdb"
ES    = Elasticsearch("http://localhost:9200")

def embed_query(q: str):
    return MODEL.encode(q).tolist()

# ── PostgreSQL: dense vector search ──────────────────────
def pg_search(q: str, k=10):
    vec = embed_query(q)
    conn = psycopg2.connect(PG)
    cur = conn.cursor()
    cur.execute("""
        SELECT id::text, content, source,
               1 - (embedding <=> %s::vector) AS score
        FROM documents
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (str(vec), str(vec), k))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [{"id": r[0], "content": r[1], "source": r[2], "score": float(r[3])} for r in rows]

# ── Elasticsearch: BM25 keyword search ───────────────────
def es_search(q: str, k=10):
    res = ES.search(index="rag_documents", body={
        "query": {"match": {"content": {"query": q, "operator": "or"}}},
        "size": k
    })
    return [{
        "id":      h["_id"],
        "content": h["_source"]["content"],
        "source":  h["_source"]["source"],
        "score":   h["_score"]
    } for h in res["hits"]["hits"]]

# ── Weaviate: hybrid (vector + BM25) ─────────────────────
def weaviate_search(q: str, k=10):
    client = weaviate.connect_to_local(host="localhost", port=8080)
    col = client.collections.get("RagDocument")
    vec = embed_query(q)
    results = col.query.hybrid(
        query=q,
        vector=vec,
        alpha=0.5,          # 0=BM25, 1=vector, 0.5=balanced
        limit=k
    )
    client.close()
    return [{
        "id":      str(r.uuid),
        "content": r.properties["content"],
        "source":  r.properties["source"],
        "score":   r.metadata.score if r.metadata else 0.5
    } for r in results.objects]

# ── Reciprocal Rank Fusion ────────────────────────────────
def rrf_fuse(*result_lists, k=60):
    scores: dict[str, float]  = {}
    docs:   dict[str, dict]   = {}
    for results in result_lists:
        for rank, doc in enumerate(results, 1):
            did = doc["id"]
            scores[did] = scores.get(did, 0) + 1 / (k + rank)
            docs[did] = doc
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [{"rrf_score": s, **docs[did]} for did, s in ranked]

# ── Main entry point ──────────────────────────────────────
def hybrid_search(query: str, top_k=5):
    pg_res      = pg_search(query)
    es_res      = es_search(query)
    wv_res      = weaviate_search(query)
    fused       = rrf_fuse(pg_res, es_res, wv_res)
    return fused[:top_k]