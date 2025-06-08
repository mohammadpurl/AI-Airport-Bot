import os
from openai import OpenAI
from typing import Optional, Dict, Any
from api.services.google_sheets_service import GoogleSheetsService
from dotenv import load_dotenv


class OpenAIService:
    def __init__(self):
        # Ensure environment variables are loaded
        load_dotenv(override=True)

        # Get API key and verify it exists
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        self.client = (
            OpenAI()
        )  # The API key is automatically read from OPENAI_API_KEY environment variable
        self.sheets_service = GoogleSheetsService()

    def get_response(self, user_input: str, knowledge_base: str) -> Dict[str, Any]:
        """Get response from OpenAI based on user input and knowledge base."""
        try:
            # Detect if the question is in Persian
            is_persian = any("\u0600" <= char <= "\u06ff" for char in user_input)

            # Create a more detailed prompt with the knowledge base
            prompt = f"""You are a helpful AI assistant for an airport information system. Your task is to answer questions based on the provided knowledge base.

Knowledge Base:
{knowledge_base}

User Question: {user_input}

Instructions:
1. First, carefully analyze the user's question and find relevant information in the knowledge base
2. If you find a direct match or closely related information, provide that answer
3. If you can't find relevant information in the knowledge base, provide a general knowledge answer in 5-6 sentences
4. If the question is in Persian, respond in Persian. If it's in English, respond in English
5. Be specific and concise in your answers
6. Always maintain a professional and helpful tone

Please provide your answer based on these instructions."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful airport information assistant. Your primary goal is to provide accurate information from the knowledge base. If the information is not available, provide a general knowledge answer. Respond in the same language as the question.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Lower temperature for more focused responses
                max_tokens=500,
            )

            answer = response.choices[0].message.content

            # Get properly formatted context data
            context_items = self.sheets_service.get_context_for_response()

            # Ensure all context items are strings and join them
            context_str = "\n".join([str(item) for item in context_items])

            # Calculate confidence score based on answer content
            confidence_score = 0.8
            if "not available" in answer.lower() or "cannot find" in answer.lower():
                confidence_score = 0.3
            elif "sorry" in answer.lower():
                confidence_score = 0.5

            return {
                "answer": answer,
                "confidence_score": confidence_score,
                "error_message": None,
                # "context_used": context_str
            }

        except Exception as e:
            return {
                "answer": None,
                "confidence_score": 0.0,
                "error_message": str(e),
                # "context_used": ""
            }
