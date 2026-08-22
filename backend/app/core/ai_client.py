import os
from openai import OpenAI
from typing import List, Dict, Any

class AIClient:
    """Simple wrapper for OpenAI API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    def get_completion(self, system_prompt: str, user_prompt: str) -> str:
        # MOCK MODE if no API key
        if not self.client:
            return self._get_mock_response(user_prompt)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI Error: {str(e)}"

    def _get_mock_response(self, question: str) -> str:
        """Simulate an intelligent response for testing purposes"""
        q = question.lower()
        if "conflict" in q:
            return "[MOCK] I have analyzed the requirements and found no direct logical conflicts. However, I suggest checking if the 'Loyalty Points' logic overlaps with 'Discount Coupons' in your database schema."
        if "missing" in q or "suggest" in q:
            return "[MOCK] Based on your project domain, I suggest adding: 1. A Password Reset flow, 2. Push Notifications for order updates, and 3. Multi-language support for international users."
        if "security" in q:
            return "[MOCK] Security Recommendation: Ensure all API endpoints are protected by JWT tokens (which DocuForge already does!) and implement Rate Limiting to prevent brute-force attacks on the login page."
        
        return f"[MOCK Assistant] I received your question: '{question}'. Once you add a real OpenAI API Key, I will be able to perform deep reasoning on your project data. For now, I can confirm that your project structure is correctly set up!"

# Singleton instance
ai_client = AIClient()
