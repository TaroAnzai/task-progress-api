# progress/ai/gemini_client.py

import os
import google.generativeai as genai
from app.ai.ai_suggestion_client import AISuggestionClient

class GeminiAISuggestionClient(AISuggestionClient):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ["GOOGLE_API_KEY"]
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")  # または "gemini-pro"

    def call_api(self, prompt: str) -> str:
        
        try:
            print(f"[GeminiClient] Sending prompt:\n{prompt}")
            response = self.model.generate_content(prompt)
            print(f"[GeminiClient] Received response:\n{response.text}")
            return response.text.strip()
        except Exception as e:
            print(f"[GeminiClient ERROR] {e}")
            raise RuntimeError(f"Gemini API 呼び出し中にエラーが発生しました: {str(e)}")



