import psycopg2, json
from psycopg2.extras import execute_values

PG_CONN = "postgresql://rag:ragpass@postgres:5432/ragdb"

def write_to_postgres(chunks):
    conn = psycopg2.connect(PG_CONN)
    cur = conn.cursor()
    rows = [(c["source"], c["chunk_index"], c["content"],
             json.dumps(c["embedding"]), json.dumps({"source": c["source"]}))
            for c in chunks]
    execute_values(cur, """
        INSERT INTO documents (source, chunk_index, content, embedding, metadata)
        VALUES %s
        ON CONFLICT DO NOTHING
    """, rows, template="(%s, %s, %s, %s::vector, %s::jsonb)")
    conn.commit()
    cur.close(); conn.close()