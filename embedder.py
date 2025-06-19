import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings  # Updated import
from langchain_community.vectorstores import FAISS, Chroma

def chunk_and_embed(text, doc_id, persist_dir="data/vectorstore", db_type="faiss"):
    """
    Splits text into chunks, embeds them, and stores in a vector DB (FAISS or Chroma).
    Args:
        text (str): The contract text to embed.
        doc_id (str): Unique identifier for the document.
        persist_dir (str): Directory to store the vector DB.
        db_type (str): 'faiss' or 'chroma'.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(text)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  # Local, no API needed
    if not os.path.exists(persist_dir):
        os.makedirs(persist_dir)
    if db_type == "faiss":
        db = FAISS.from_texts(chunks, embeddings, metadatas=[{"doc_id": doc_id}] * len(chunks))
        db.save_local(persist_dir)
    elif db_type == "chroma":
        db = Chroma.from_texts(chunks, embeddings, metadatas=[{"doc_id": doc_id}] * len(chunks), persist_directory=persist_dir)
        db.persist()
    else:
        raise ValueError("db_type must be 'faiss' or 'chroma'")
    print(f"Stored {len(chunks)} chunks for {doc_id} in {db_type} vector DB.")

def load_vectorstore(persist_dir="data/vectorstore", db_type="faiss"):
    """
    Loads the vector store for querying.
    Args:
        persist_dir (str): Directory where the vector DB is stored.
        db_type (str): 'faiss' or 'chroma'.
    Returns:
        VectorStore instance.
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    if db_type == "faiss":
        return FAISS.load_local(persist_dir, embeddings)
    elif db_type == "chroma":
        return Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    else:
        raise ValueError("db_type must be 'faiss' or 'chroma'")