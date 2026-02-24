# Script to setup running on Window 
## Updated for Python 3.13 compatibility (run on Git Bash)
```bash
cd rag_project/

python -m venv venv
source venv/Scripts/activate

pip install -r requirements.txt
## Verify installation:
python -c "import sklearn, pandas, numpy; print('All packages available')"
```

1. Types of Keyword Search
```bash
python tfidf_search.py
python bm25_search.py
python compare_methods.py
## Hybrid of Keyword search ?
python hybrid_search.py
```

2. Embedding
```bash
python keyword_limitation_demo.py
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org sentence-transformers
pip install openai
python -c "import sentence_transformers, openai; print('Embedding packages available')"
python semantic_search_demo.py
```

3. Vectore Database
```bash
pip install chromadb
python -c "import chromadb; print('ChromaDB available')"

python init_vectordb.py ##still stuck in here

python store_documents.py

python vector_search_demo.py

python save_vectordb.py
python check_persistence.py


```