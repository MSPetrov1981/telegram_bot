import requests


class MistralAPIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.mistral.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def chat_completion(self, model, messages, max_tokens=500, temperature=0.7):
        """Make chat completion request to Mistral API"""
        url = f"{self.base_url}/chat/completions"

        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Mistral API request failed: {e}")
            return "I'm sorry, I'm having trouble processing your request right now."
