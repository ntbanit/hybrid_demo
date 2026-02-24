#!/usr/bin/env python3
"""
Simple TF-IDF Search Demo
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys 
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils import get_doc_info


print("🔍 TF-IDF Search Demo")
print("=" * 50)

# Load documents from techcorp-docs
docs, doc_paths = get_doc_info()

# Create TF-IDF matrix
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(docs)

# Example searches
queries = ["remote work policy", "health insurance benefits", "pet policy dogs"]

for query in queries:
    print(f"🔎 Searching for: '{query}'")
    
    # Transform query to TF-IDF
    query_vector = vectorizer.transform([query])
    
    # Calculate similarities
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    
    # Get top results
    top_indices = similarities.argsort()[-3:][::-1]
    
    print("Results:")
    for i, idx in enumerate(top_indices, 1):
        # Show only document path and score
        doc_name = doc_paths[idx].split('/')[-1]  # Just the filename
        print(f"  {i}. Score: {similarities[idx]:.4f} - {doc_name}")
    print()

print("✅ TF-IDF search completed!")