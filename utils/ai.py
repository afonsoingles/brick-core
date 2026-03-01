import os
import openai

class AI:
    def __init__(self):
        self.key = os.environ.get("AI_KEY")
        self.base_url = os.environ.get("AI_URL")
        self.client = openai.OpenAI(api_key=self.key, base_url=self.base_url)

    def get(self, prompt, model="google/gemini-2.5-flash-lite-preview-09-2025"):
        response = self.client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        return response.choices[0].message.content