from app.rag.document_loader import load_and_chunk_pdf
from app.rag.vector_store import build_vector_store
from app.rag.rag_chain import answer_from_pdf

chunks = load_and_chunk_pdf("test.pdf")
vector_store = build_vector_store(chunks)

question = "What is this person's CGPA?"
answer = answer_from_pdf(vector_store, question)

print(f"Question: {question}")
print(f"Answer: {answer}")