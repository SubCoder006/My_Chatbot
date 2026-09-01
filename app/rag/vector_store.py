from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def build_vector_store(chunks):
    vector_store = FAISS.from_documents(chunks, embeddings)
    return vector_store

def get_relevant_chunks(vector_store,question, k=3):
    results = vector_store.similarity_search(question, k=k)
    return results