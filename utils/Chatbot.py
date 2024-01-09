import random
import requests

class Chatbot:

    def __init__(self) -> None:

         # +++A valid huggingface token is needed here+++
        self.API_TOKEN = "YOUR_HUGGINGFACE_ACCESS_TOKEN" 
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

    def call_T5(self, message) -> str:
        API_URL = "https://api-inference.huggingface.co/models/t5-large"

        headers = {"Authorization": f"Bearer {self.API_TOKEN}"}
        response = requests.post(API_URL, headers = headers, json = message)
        return [response.json(), "translation_text"]    
    

    def call_BART(self, message) -> str:
        API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

        headers = {"Authorization": f"Bearer {self.API_TOKEN}"}
        response = requests.post(API_URL, headers = headers, json = message)
        return [response.json(), "summary_text"]