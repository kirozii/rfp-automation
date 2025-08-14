from langchain_core.messages import HumanMessage, SystemMessage
from openai import AsyncAzureOpenAI
import PyPDF2
import fitz
import os
from pydantic import SecretStr
from ..core.config import settings
from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI

class Generator:
    def __init__(self):
        """
        Initializes the LLM model.
        """
        key = SecretStr(settings.AZURE_OPENAI_KEY)
        if not key:
            raise ValueError("Gemini API key not found.")
        endpoint = SecretStr(settings.AZURE_OPENAI_ENDPOINT)
        if not endpoint:
            raise ValueError("Azure OpenAI endpoint not found.")
        self._model = "gpt-4o-mini"
        self._client = AsyncAzureOpenAI(
            api_key=key.get_secret_value(),
            api_version="2025-01-01-preview",
            azure_endpoint=endpoint.get_secret_value(),
        )

        content = " "

        supported_files = self.get_all_supported_files("knowledge/")
    
        if not supported_files:
            print(" No supported files found.")
    
        for file_path in supported_files:
            print(f"\n📄 File: {file_path}")
            tempcontent = self.load_file_text(file_path)
    
            if not content or "[ERROR]" in content:
                print(f"⚠️ Could not load content from: {file_path}")
                continue
            else:
                content += tempcontent


        self.knowledge = content
        #self._model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", api_key=key)
        #self._structured_model = self._model.with_structured_output(Slide)
    async def rewrite_with_mphasis(self, question, answer):
        prompt = f"""
        Contextualize the answer and make sure there is no markdown, and a maximum of 5 points with 3 lines each are present. If the question is like "Your way of xyz", or "How would you handle it" rewrite it to sound like Mphasis is writing it. Do not use it for definitions etc, make sure the answer is contextualized and makes sense with the question.
        Return nothing but the answer.
        Response:
        Question:
        \"\"\"{question}\"\"\"

        Answer:
        \"\"\"{answer}\"\"\"

        Rewritten answer:
        """
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return response.choices[0].message.content.strip()

    def load_pdf_text(self, file_path):
        try:
            doc = fitz.open(file_path)
            return "\n".join(page.get_text() for page in doc)
        except Exception as e:
            return f"[PDF READ ERROR]: {e}"
    
    def load_txt_text(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"[TEXT READ ERROR]: {e}"
    
    def load_pptx_text(self, file_path):
        try:
            prs = Presentation(file_path)
            text = ""
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text += shape.text + "\n"
            return text
        except Exception as e:
            return f"[PPT READ ERROR]: {e}"
    
    def load_file_text(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return self.load_pdf_text(file_path)
        elif ext == ".txt":
            return self.load_txt_text(file_path)
        elif ext in [".ppt", ".pptx"]:
            return self.load_pptx_text(file_path)
        return None

    def get_all_supported_files(self, root_folder, extensions=[".pdf", ".txt", ".ppt", ".pptx"]):
        matched_files = []
        for root, dirs, files in os.walk(root_folder):
            for file in files:
                if os.path.splitext(file)[1].lower() in extensions:
                    matched_files.append(os.path.join(root, file))
        return matched_files

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
        prompt = f"""You are an assistant who generates answers for users. Answer the following question in around 3 points with around 3 lines each. Do not use any markdown. The document is provided as a reference, if the answer is not found in it use your knowledge to answer it. Do not specify that you did not find the answer in the document. Simply provide the answer.

        Document:
        {self.knowledge}
        
        Question: {question}

        ######
        Use a maximum of 4 points with 3 lines each.
        Answer:"""
    
        print("LLM: Generating response for question: " + question)
        print("API Key:", self._client.api_key)
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        content = response.choices[0].message.content.strip()
        print(content)
        content = await self.rewrite_with_mphasis(question, content)
        content = content.replace("\n\n", "\n")
        return {"Answer": content}
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
