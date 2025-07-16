from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import SecretStr
import re
from ..core.config import settings
from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI

class Generator:
    def __init__(self):
        """
        Initializes the LLM model.
        """
        key = SecretStr(settings.GEMINI_API_KEY)
        if not key:
            raise ValueError("Gemini API key not found.")

        self._model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=key)

    async def generate_response(self, question: str) -> Dict:
        """
        Generate a response to a given question.

        Args:
            question: The question we need to generate a response for.

        Returns:
            Dictionary in the format {"Answer": response}
        """
        messages = [
            SystemMessage(content="You are a technical assistant. Provide a concise answer. Aim for 150-200 words."),
        #     HumanMessage(content=f"""
        #         Question: {question}.
        #         Structure your response as follows:
        #
        #         Answer: [concise answer]
        #         Solution: [step-by-step solution]
        #         Implementation: [code if applicable] 
        #         TechStack: [comma-seperated technologies]
        #     """)
            HumanMessage(content=question)
        ]
        print("LLM: Generating response for question: " + question)
        response = await self._model.ainvoke(messages)
        return self._parse_responses(response.content)

    def _parse_responses(self, text) -> Dict:
        """
        Creates a dictionary with the response. Placeholder function for experimental use.

        Args:
            text: AI generated response

        Returns:
            Dictionary with key "Answer"
        """
        # keys = ["Answer", "Solution", "Implementation", "TechStack"]
        # key_alt = "|".join(keys)
        # pattern = rf"({key_alt}):\s*(.*?)\s*(?=(?:{key_alt}):|$)"
        # matches = re.findall(pattern, text, re.DOTALL)
        # return {k: v for k, v in matches}
        
        return {"Answer": text}
