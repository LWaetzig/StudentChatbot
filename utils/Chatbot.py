import random


class Chatbot:
    def __init__(self) -> None:
        pass

    def generate_response(self, message) -> str:
        response = random.choice(
            [
                "I don't know what you mean.",
                "I don't understand.",
                "I'm sorry, I don't know what you mean.",
                "I'm sorry, I don't understand.",
            ]
        )
        return response
