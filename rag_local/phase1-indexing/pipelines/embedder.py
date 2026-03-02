from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"   # 384-dim, fast, local
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def embed_chunks(chunks):
    model = get_model()
    texts = [c["content"] for c in chunks]
    vectors = model.encode(texts, batch_size=64, show_progress_bar=True)
    for chunk, vec in zip(chunks, vectors):
        chunk["embedding"] = vec.tolist()
    return chunks