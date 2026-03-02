CREATE DATABASE airflow_db;
\c ragdb;
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source      TEXT NOT NULL,
    chunk_index INT,
    content     TEXT NOT NULL,
    embedding   vector(384),         -- match your model dim
    metadata    JSONB,
    indexed_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);