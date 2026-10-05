import os
import requests
from dotenv import load_dotenv


load_dotenv()


class RAGGenerator:

    def __init__(self):

        self.api_key = os.getenv("GROQ_API_KEY")

        self.url = "https://api.groq.com/openai/v1/chat/completions"

        self.model = "llama-3.1-8b-instant"

        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

    def build_prompt(self, question, retrieved_results):

        context = "\n\n".join(
            [
                f"Source: {result['document']}\n"
                f"{result['text']}"
                for result in retrieved_results
            ]
        )

        prompt = f"""
You are CampusMind, an intelligent college information assistant.

Answer the user's question using ONLY the information provided
in the context.

RULES:
- Answer the user's question directly.
- Use only information from the provided context.
- Do not invent or assume information.
- If the context does not contain the answer, say:
  "The information is not available in the college knowledge base."
- Keep the answer concise and natural.
- Use complete sentences.
- Do not repeat the user's question.
- Do not mention the context, documents, retrieval, or RAG.
- If the context contains a specific date, number, rule,
  or requirement, preserve it exactly.

CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""

        return prompt

    def generate_answer(self, prompt):

        response = requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.2,
                "max_tokens": 300
            },
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"].strip()