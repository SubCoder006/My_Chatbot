from app.llm.groq_client import get_reply
from app.rag.rag_chain import answer_from_pdf
class ChatService:
    def __init__(self, memory):
        self.memory = memory

    def send(self, user_input):
        self.memory.add_user_message(user_input)
        try:
            reply = get_reply(self.memory.get_messages())
            self.memory.add_assistant_message(reply)
            return reply
        except Exception as e:
            self.memory.undo_last_user_message()
            raise e

    def send_with_pdf(self, user_input, vector_store):
        self.memory.add_user_message(user_input)
        try:
            reply = answer_from_pdf(vector_store, user_input)
            self.memory.add_assistant_message(reply)
            return reply
        except Exception as e:
            self.memory.undo_last_user_message()
            raise e
    