
from app.core.memory import ConversationMemory
from app.services.chat_service import ChatService

memory = ConversationMemory()
chat_service = ChatService(memory)

print("Chatbot ready! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    
    memory.add_user_message(user_input)
    
    try:
        reply = chat_service.send(user_input)
        print(f"Bot: {reply}\n")

    except Exception as e:
        print(f"Something went wrong: {e}\n")

