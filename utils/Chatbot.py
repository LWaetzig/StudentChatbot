import requests
import json

# TODO: implement condition, that error messages sent from the model (e.g.:{"error":"Model t5-large is currently loading","estimated_time":118.0269775390625}) are displayed in the chat

class Chatbot:
    def __init__(self, model: str, api_token: str) -> None:
        self.API_TOKEN = api_token
        self.model = model
        if self.model == "T5":
            self.API_URL = "https://api-inference.huggingface.co/models/t5-large"
        elif self.model == "BART":
            self.API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        elif self.model == "QA_BERTA":
            self.API_URL = "https://api-inference.huggingface.co/models/timpal0l/mdeberta-v3-base-squad2"

    def generate_response(self, message: str) -> str:
        headers = {"Authorization": f"Bearer {self.API_TOKEN}"}
        message = {"inputs": message, "parameters": {"num_beams": 3}}
        response = requests.post(self.API_URL, headers=headers, json=message)
        print(response.text) # only used for bugfixing
        response_data = json.loads(response.text)

        if isinstance(response_data, dict) and "error" in response_data:
            return f"Error in model response: {response_data['error']}"
        
        if response.status_code == 200:
            if self.model == "T5":
                return response.json()[0].get("translation_text")
            elif self.model == "BART":
                return response.json()[0].get("summary_text")
            elif self.model == "QA_BERTA":
                return response.json().get("answer")
        else:
            return "Error: Could not generate response. Maybe check your API Token?"
