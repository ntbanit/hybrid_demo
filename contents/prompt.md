Write for me ouput is a .MD file which has this content, target audience is a non-technical ones, and junior developers, so each part should have 3-5 examples in **#examples#** part or demo in **#diagram#**, brief explain  **#explain#** in the language everyone can understand , which illustrating by Mermaid/ SVG inline in .MD file


- Topic : Hybrid Search: Combining keyword and vector search for accuracy
- Outline :
1. Why Vector Search Alone Is Not Enough 
a. Vector Search definition 
	**#examples#** of Vector Search
	**#explain#** some algorithms of Vector Search + **#examples#** 
b. Keyword Search definition 
	**#examples#** of Keyword Search
	**#explain#** some algorithms of Keyword Search + **#examples#** 
	
c. Hybrid Search definition
	**#explain#** + **#examples#** Keyword Search-alone limitation : frustrating user 
	**#explain#** + **#examples#** Vector Search-alone limitation : struggle with specific keyword, Lack of Domain & Business Knowledge, Temporal Context (Time Sensitive)
	**#explain#** + **#examples#** Hybrid Search can ultize the strength of both techniques 
		
2. Hybrid Search workflow

**Parallel Querying:** The system sends the user's query to both the vector index and a traditional keyword index (like Elasticsearch or Lucene) simultaneously.
**Independent Scoring:** Each system produces its own set of results with its own scoring scale (vectors use similarity scores like Cosine Similarity, while keywords use counts like BM25).
**Score Normalization & Fusion:** This is the biggest change. Since you can't easily compare a vector score of `0.85` to a BM25 score of `12.4`, the system uses a fusion algorithm—most commonly **Reciprocal Rank Fusion (RRF)**—to merge the lists.
**Re-ranking (Optional but Common):** A "Cross-Encoder" model may look at the merged top results to provide a final, highly accurate ranking before sending the data to the LLM.

**#diagram#** of above parts

**#examples#** with some docs and text 

**#diagram#** compare RRF with Weighted Sum Fusion approach, when to use which 

3. Hybrid Search in RAG Pipelines
**#diagram#**  compare the AS-IS and TO-BE 

Phase 1: Index : as-is : 
- Document chunking
- Vector database storage

Phase 2: Retrieval:as-is : 
- Query processing
- Vector search
- Context augmentation
- Response generation

Phase 1: Index : to-be : 
- Document chunking
- Vector database storage
- Keyword/Metadata database storage


Phase 2: Retrieval: to-be : 
- Query processing
- hybrid search
- Context augmentation
- Response generation

**#explain#** which DB support Dense / Sparse : PostgreSQL, ElasticSearch, Weaviate, Pinecone, Milvus, Qdrant... 
when to use which 

**#explain#** + **#examples#** challenging with hybrid search 
Dual Index Synchronization
Chunking Strategy Affects Both Indexes Differently
Score Normalization Before Fusion
Fusion Weight Tuning (α)
Latency: Two Searches in Parallel

################################################################
