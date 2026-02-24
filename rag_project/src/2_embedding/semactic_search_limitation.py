# This script demonstrates the limitations of semantic search when applied to the `general_faqs.md` file.

import sys 
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils import read_techcorp_docs

print("🔍 Semantic Search Limitations Demo")
print("=" * 50)

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

# Perform semantic search and demonstrate limitations
def demonstrate_semantic_search_limitations(query):
    """Perform semantic search and highlight its limitations."""
    
    print("\nQuery:", query)
    semantic_search(query)
    # Highlight limitations
    print("\nLimitations:")
    print("1. Semantic search may return results that are contextually relevant but not directly answering the query.")
    print("2. It may struggle with domain-specific terminology or uncommon phrases.")
    print("3. Results ranking may not always prioritize the most accurate answer.")

if __name__ == "__main__":
    # Example query
    query = "What is the phone 1-800-832-4267 using for?"

    # Demonstrate semantic search limitations
    demonstrate_semantic_search_limitations(query)