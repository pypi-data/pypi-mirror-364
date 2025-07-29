import requests
from typing import List

class AIChat:
    def __init__(self, token: str, model: str = "gemini-pro"):
        """
        Initialize AIChat with Gemini API token and model name.
        """
        self.api_key = token
        self.model = model
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def get_response(self, history: List[str]) -> str:
        """
        Get AI response from a conversation history.

        Parameters:
            history (List[str]): Must alternate [user, ai, user, ai...]

        Returns:
            str: AI-generated response
        """
        if len(history) % 2 == 0:
            raise ValueError("History must have odd length: alternating user and AI messages.")

        # Construct messages
        contents = []
        for i, msg in enumerate(history):
            role = "user" if i % 2 == 0 else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg}]
            })

        headers = {
            "Content-Type": "application/json"
        }

        body = {
            "contents": contents
        }

        response = requests.post(self.api_url, headers=headers, json=body)

        if response.status_code != 200:
            raise Exception(f"Error from Gemini API: {response.status_code} {response.text}")

        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
