import random
import requests

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

    def call_t5_model(self, message) -> str:
        API_URL = "https://api-inference.huggingface.co/models/t5-large"
        
        # +++A valid huggingface token is needed here+++
        API_TOKEN = "PASTE_YOUR_HUGGINGFACE_ACCESS_TOKEN_HERE" 

        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        response = requests.post(API_URL, headers = headers, json = message)
        return response.json()