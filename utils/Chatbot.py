import requests

# TODO: implement condition, that error messages sent from the model (e.g.:{"error":"Model t5-large is currently loading","estimated_time":118.0269775390625}) are displayed in the chat

class Chatbot:
    def __init__(self, model: str, api_token: str) -> None:
        self.API_TOKEN = api_token
        self.model = model
        if self.model == "T5":
            self.API_URL = "https://api-inference.huggingface.co/models/t5-large"
        elif self.model == "BART":
            self.API_URL = (
                "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
            )

    def generate_response(self, message: str) -> str:
        headers = {"Authorization": f"Bearer {self.API_TOKEN}"}
        message = {"inputs": message, "parameters": {"num_beams": 3}}
        response = requests.post(self.API_URL, headers=headers, json=message)
        print(response.text) # only used for bugfixing
        if response.status_code == 200:
            if self.model == "T5":
                return response.json()[0].get("translation_text")
            elif self.model == "BART":
                return response.json()[0].get("summary_text")
        else:
            return "Error: Could not generate response. Maybe check your API Token?"
