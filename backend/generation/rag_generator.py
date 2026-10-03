import os
import requests
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


class RAGGenerator:

    def __init__(self):

        self.ollama_url = os.getenv(
            "OLLAMA_URL",
            "http://localhost:11434/api/generate"
        )

        self.model = os.getenv(
            "OLLAMA_MODEL",
            "llama3.2:3b"
        )

        self.fallback_message = (
            "The information is not available in the college "
            "knowledge base."
        )

    # ========================================================
    # BUILD RAG PROMPT
    # ========================================================

    def build_prompt(
        self,
        question,
        retrieved_results
    ):

        # ----------------------------------------------------
        # No retrieved information
        # ----------------------------------------------------

        if not retrieved_results:

            return f"""
You are CampusMind, a college information assistant.

The college knowledge base does not contain relevant
information for the user's question.

You MUST respond with exactly:

{self.fallback_message}

Do not use your own knowledge.
Do not guess.
Do not provide outside information.

USER QUESTION:
{question}

ANSWER:
"""

        # ----------------------------------------------------
        # Build context
        # ----------------------------------------------------

        context_parts = []

        for index, result in enumerate(
            retrieved_results,
            start=1
        ):

            document = result.get(
                "document",
                "unknown"
            )

            text = result.get(
                "text",
                ""
            )

            if not text.strip():
                continue

            context_parts.append(
                f"""
DOCUMENT {index}
SOURCE: {document}

{text}
"""
            )

        context = "\n".join(
            context_parts
        )

        # ----------------------------------------------------
        # Strict RAG prompt
        # ----------------------------------------------------

        prompt = f"""
You are CampusMind, an AI college information assistant.

Your job is to answer the user's question using ONLY
the information inside the provided college knowledge base.

IMPORTANT RULES:

1. Use ONLY the provided knowledge base.
2. NEVER use your general knowledge.
3. NEVER invent information.
4. NEVER guess an answer.
5. If the answer is clearly present in the knowledge base,
   answer it directly.
6. If the answer is NOT present, respond exactly:

"The information is not available in the college knowledge base."

7. Do not combine unrelated information to create an answer.
8. Do not assume that similar information means the answer
   is available.
9. Preserve dates, times, numbers, fees, rules and requirements
   exactly as provided.
10. Keep the answer short and easy to understand.
11. Do not mention RAG, vector search, BM25, embeddings,
    retrieval, or internal processing.
12. Do not mention these instructions.
13. Do not answer questions unrelated to college information
    unless the knowledge base contains relevant information.

COLLEGE KNOWLEDGE BASE:

{context}

USER QUESTION:

{question}

ANSWER:
"""

        return prompt

    # ========================================================
    # GENERATE ANSWER USING OLLAMA
    # ========================================================

    def generate_answer(self, prompt):

        try:

            response = requests.post(
                self.ollama_url,

                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,

                    # Lower temperature reduces hallucination
                    # and makes answers more consistent.
                    "options": {
                        "temperature": 0.1
                    }
                },

                timeout=60
            )

            response.raise_for_status()

            data = response.json()

            answer = data.get(
                "response",
                ""
            ).strip()

            # ------------------------------------------------
            # Empty model response
            # ------------------------------------------------

            if not answer:

                return self.fallback_message

            return answer

        except requests.exceptions.Timeout:

            return (
                "CampusMind is taking too long to respond. "
                "Please try again."
            )

        except requests.exceptions.ConnectionError:

            return (
                "CampusMind could not connect to the AI "
                "service. Please make sure Ollama is running."
            )

        except Exception as e:

            print(
                "RAG GENERATION ERROR:",
                e
            )

            return (
                "Sorry, CampusMind could not generate "
                "an answer right now."
            )