from elasticsearch import Elasticsearch, helpers

ES = Elasticsearch("http://elasticsearch:9200")
INDEX = "rag_documents"

def ensure_index():
    if not ES.indices.exists(index=INDEX):
        ES.indices.create(index=INDEX, body={
            "mappings": {
                "properties": {
                    "source":      {"type": "keyword"},
                    "chunk_index": {"type": "integer"},
                    "content":     {"type": "text", "analyzer": "english"}
                }
            }
        })

def write_to_elasticsearch(chunks):
    ensure_index()
    actions = [{
        "_index": INDEX,
        "_id": f"{c['source']}_{c['chunk_index']}",
        "_source": {
            "source":      c["source"],
            "chunk_index": c["chunk_index"],
            "content":     c["content"]
        }
    } for c in chunks]
    helpers.bulk(ES, actions)