from app.rag.document_loader import load_and_chunk_pdf

chunks = load_and_chunk_pdf("test.pdf")

print(f"Total chunks: {len(chunks)}\n")
print("--- First chunk ---")
print(chunks[0].page_content)
print("\n--- Metadata ---")
print(chunks[0].metadata)