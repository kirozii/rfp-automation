from langchain_core.messages import HumanMessage, SystemMessage
import PyPDF2
from pydantic import SecretStr
from ..core.config import settings
from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from ..schemas.powerpoint_response import Slide

class Generator:
    def __init__(self):
        """
        Initializes the LLM model.
        """
        key = SecretStr(settings.GEMINI_API_KEY)
        if not key:
            raise ValueError("Gemini API key not found.")

        self._model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", api_key=key)
        self._structured_model = self._model.with_structured_output(Slide)

    def read_pdf(self, pdf_path):
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n"
        except FileNotFoundError:
            print(f"Error: The file '{pdf_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
        return text

    async def generate_response(self, question: str) -> Dict:
        """
        Generate a response to a given question.

        Args:
            question: The question we need to generate a response for.

        Returns:
            Dictionary in the format {"Answer": response}
        """
        filename = "knowledge/reference.pdf"
        file_content = self.read_pdf(filename)
        print(file_content)
        messages = [
            SystemMessage(content="You are a technical assistant. Provide a concise answer and nothing else. Use the document as reference. Aim for 3 points, around 3 lines each. Do not use any bold/italics."),
            HumanMessage(content=f"""
                Document: {file_content}
                #######
                Question: {question}
            """)
        ]
        print("LLM: Generating response for question: " + question)
        response = await self._model.ainvoke(messages)
        print(response)
        response.content = response.content.replace("\n\n", "\n")
        print(response.content)
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
