from langchain_core.prompts import ChatPromptTemplate
from app.llm.groq_client import llm
from app.rag.vector_store import get_relevant_chunks

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Answer the question using ONLY the context below. "
     "If the answer isn't in the context, say don't know.\n\n"
     "Context:\n{context}"),
    ("human","{question}"),
])

rag_chain = RAG_PROMPT | llm

def answer_from_pdf(vector_store, question):
    relevant_docs = get_relevant_chunks(vector_store, question)
    context = "\n\n".join(doc.page_content for doc in relevant_docs)
    
    response = rag_chain.invoke({
        "context": context,
        "question": question,
    })
    return response.content