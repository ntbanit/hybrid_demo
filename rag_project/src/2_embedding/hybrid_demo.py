import sys 
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils import read_techcorp_docs

# Load documents (without verbose output)
docs, doc_paths = read_techcorp_docs()
# Load local embedding model
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings for all documents
doc_embeddings = model.encode(docs)

import numpy as np
def semantic_search(query):

    # Generate embedding for query
    query_embedding = model.encode([query])

    # Calculate cosine similarities
    similarities = np.dot(query_embedding, doc_embeddings.T).flatten()

    # Get top results
    top_indices = similarities.argsort()[-3:][::-1]

    print("Results:")
    for i, idx in enumerate(top_indices, 1):
        doc_name = doc_paths[idx].split('/')[-1]
        print(f"  {i}. Score: {similarities[idx]:.4f} - {doc_name}")

    # Check if we found relevant documents
    if similarities[top_indices[0]] > 0.3:
        print("  ✅ Found relevant documents!")
    else:
        print("  ❌ No relevant documents found!")

query = "What is the phone 1-800-832-4267 using for?"
semantic_search(query)

from rank_bm25 import BM25Okapi
import re

import sys 
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.stdout.reconfigure(encoding='utf-8')
from utils import get_doc_info

print("🔍 BM25 Search Demo")
print("=" * 50)

# Load documents from techcorp-docs
docs, doc_paths = get_doc_info()
print(f"📚 Loaded {len(docs)} documents\n")

# Tokenize documents
tokenized_docs = [re.sub(r'[^a-zA-Z\s]', '', doc.lower()).split() for doc in docs]

# Create BM25 index
bm25 = BM25Okapi(tokenized_docs)

# Example searches
queries = [query]

for query in queries:
    print(f"🔎 Searching for: '{query}'")
    
    # Tokenize query
    tokenized_query = re.sub(r'[^a-zA-Z\s]', '', query.lower()).split()
    
    # Get BM25 scores
    scores = bm25.get_scores(tokenized_query)
    
    # Get top results
    top_indices = scores.argsort()[-3:][::-1]

        
    print("Results:")
    for i, idx in enumerate(top_indices, 1):
        # Show only document path and score
        doc_name = doc_paths[idx].split('/')[-1]  # Just the filename
        print(f"  {i}. Score: {scores[idx]:.4f} - {doc_name}")
    print()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

print("🤖 Agentic Chunking Demo")
print("=" * 50)

# Configuration - using environment variables for API access
API_KEY = os.environ.get("GEMINI_API_KEY")
API_BASE = os.environ.get("GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta/openai/")
MODEL_NAME = "gemini-2.5-flash-lite"
llm = ChatOpenAI(
        model=MODEL_NAME,
        openai_api_key=API_KEY,
        openai_api_base=API_BASE,
        temperature=0  # Deterministic output for consistency
)