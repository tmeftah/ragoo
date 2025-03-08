import requests
from typing import List
import json
from ragoo.core.config import settings


class OllamaHandler:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = settings.OLLAMA_HOST or base_url
        self.model = settings.COMPLETION_MODEL

    def generate_completion(self, prompt: str, **kwargs) -> str:
        """Generate text completion using Ollama"""
        try:
            url = f"{self.base_url}/api/generate"
            headers = {"Content-Type": "application/json"}
            data = {"model": self.model, "prompt": prompt, "stream": False}

            response = requests.post(url, headers=headers, data=json.dumps(data))

            response.raise_for_status()

            # Handle streaming response if needed
            if response.headers.get("Content-Type") == "application/json":
                return response.json().get("response", "")

            # For non-streaming response
            full_response = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    full_response += chunk.get("response", "")
                    if chunk.get("done"):
                        break
            return full_response

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")
