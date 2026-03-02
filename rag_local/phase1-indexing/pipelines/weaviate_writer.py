import weaviate

client = weaviate.connect_to_local(host="weaviate", port=8080)
CLASS_NAME = "RagDocument"

def ensure_schema():
    existing = [c.name for c in client.collections.list_all().values()]
    if CLASS_NAME not in existing:
        client.collections.create(
            name=CLASS_NAME,
            vectorizer_config=weaviate.classes.config.Configure.Vectorizer.none(),
            properties=[
                weaviate.classes.config.Property(name="source",      data_type=weaviate.classes.config.DataType.TEXT),
                weaviate.classes.config.Property(name="chunk_index", data_type=weaviate.classes.config.DataType.INT),
                weaviate.classes.config.Property(name="content",     data_type=weaviate.classes.config.DataType.TEXT),
            ]
        )

def write_to_weaviate(chunks):
    ensure_schema()
    col = client.collections.get(CLASS_NAME)
    with col.batch.dynamic() as batch:
        for c in chunks:
            batch.add_object(
                properties={"source": c["source"], "chunk_index": c["chunk_index"], "content": c["content"]},
                vector=c["embedding"]
            )