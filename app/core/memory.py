from app.config import SYSTEM_PROMPT, MAX_HISTORY_MESSAGES


class ConversationMemory:
    def __init__(self):
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def add_user_message(self, content):
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content):
        self.messages.append({"role": "assistant", "content": content})
        self._trim()

    def undo_last_user_message(self):
        # called when a request fails, so we don't keep a dangling unanswered message
        if self.messages and self.messages[-1]["role"] == "user":
            self.messages.pop()

    def _trim(self):
        if len(self.messages) > MAX_HISTORY_MESSAGES + 1:
            self.messages[:] = [self.messages[0]] + self.messages[-MAX_HISTORY_MESSAGES:]

    def get_messages(self):
        return self.messages
    