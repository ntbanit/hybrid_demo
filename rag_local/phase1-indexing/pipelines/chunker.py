from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=64,
    separators=["\n\n", "\n", ".", " "]
)

def chunk_documents(docs):
    chunks = []
    for doc in docs:
        parts = splitter.split_text(doc["content"])
        for i, part in enumerate(parts):
            chunks.append({
                "source": doc["source"],
                "chunk_index": i,
                "content": part
            })
    return chunks