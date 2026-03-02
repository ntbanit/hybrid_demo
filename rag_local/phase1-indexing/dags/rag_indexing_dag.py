from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
sys.path.insert(0, "/opt/airflow/pipelines")

from loader          import load_documents
from chunker         import chunk_documents
from embedder        import embed_chunks
from pg_writer       import write_to_postgres
from es_writer       import write_to_elasticsearch
from weaviate_writer import write_to_weaviate

def run_indexing():
    print("🔄 Loading documents...")
    docs   = load_documents()
    print(f"   {len(docs)} documents loaded")
    
    print("✂️  Chunking...")
    chunks = chunk_documents(docs)
    print(f"   {len(chunks)} chunks created")
    
    print("🧠 Embedding...")
    chunks = embed_chunks(chunks)
    
    print("💾 Writing to PostgreSQL...")
    write_to_postgres(chunks)
    
    print("🔍 Writing to Elasticsearch...")
    write_to_elasticsearch(chunks)
    
    print("🌐 Writing to Weaviate...")
    write_to_weaviate(chunks)
    
    print("✅ Indexing complete!")

with DAG(
    dag_id="rag_monthly_indexing",
    start_date=datetime(2024, 1, 1),
    schedule="@monthly",        # runs 1st of each month
    catchup=False,
    tags=["rag", "indexing"]
) as dag:
    PythonOperator(task_id="index_documents", python_callable=run_indexing)