from sqlalchemy.orm import Session
import asyncio
import os
import fitz
from typing import Dict, List
from pptx import Presentation
from ..core.config import settings
from pydantic import SecretStr
import logging
from openai import AsyncAzureOpenAI
from ..models import QuestionStatus
from ..crud import questions

logger = logging.getLogger("rfpai.agents.data_retrieval_agent")

class DataRetrievalAgent:
    """
    Agent responsible for retrieving relevant data via RAG and KM.
    """
    db: Session

    def __init__(self, db: Session):
        """
        Initializes an instance of the agent.

        Args:
            db (Session): An SQLAlchemy database session
        """
        self.db = db
        key = SecretStr(settings.AZURE_INFERENCE_CREDENTIAL)
        if not key:
            raise ValueError("Azure AI Foundry key not found.")
        
        endpoint = SecretStr(settings.AZURE_INFERENCE_ENDPOINT)
        if not endpoint:
            raise ValueError("Azure AI Foundry endpoint not found.")

        self._model = "gpt-4o-mini"
        self._client = AsyncAzureOpenAI(
            api_key=key.get_secret_value(),
            api_version="2025-01-01-preview",
            azure_endpoint=endpoint.get_secret_value(),
        )
        logger.info("Data Retrieval agent initialized.")

    async def process(self, question_id: int):
        """
        Retrieves data and updates the context column of the stored question.

        NOTE: This function will draft a complete response and save it in context. Need to improve the RAG system first.
        """
        logger.info("Starting data retrieval for question_id: %s", question_id)
        question = questions.get_question(self.db, question_id)
        if question is None:
            logger.error("Could not find question with question_id: %s", question_id)
            return
        questions.update_question_status(self.db, question_id, QuestionStatus.PENDING_DATA_RETRIEVAL)
        self.knowledge = self._get_context()
        response = await self.generate_response(question.question_text)
        questions.update_question_context(self.db, question_id, context=response["Answer"])
        logger.info("Data retrieval completed for question_id: %s", question_id)

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
    
        logger.info("LLM: Generating response for question: %s", question)
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        content = response.choices[0].message.content.strip()
        logger.info("LLM: Generated response for question: %s", question)
        content = content.replace("\n\n", "\n")
        return {"Answer": content}

    def _get_context(self):
        """
        Retrieves the context of the question.

        NOTE: Currently it just reads everything in /knowledge and returns all the text. Will change once vector db is implemented.
        """
        files = self.get_all_supported_files("knowledge/")
        context = ""
        for file in files:
            tempcontent = self._load_file_text(file)
    
            if not tempcontent or "[ERROR]" in tempcontent:
                print(f"⚠️ Could not load content from: {file}")
                continue
            context += tempcontent + "\n"
        return context

    def _load_file_text(self, file_path):
        """
        Loads the text from the file.

        Args:
            file_path (str): The path to the file.

        Returns:
            str: The text from the file.
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return self._load_pdf_text(file_path)
        elif ext == ".txt":
            return self._load_txt_text(file_path)
        elif ext in [".ppt", ".pptx"]:
            return self._load_pptx_text(file_path)
        return None

    def get_all_supported_files(self, root_folder, extensions=[".pdf", ".txt", ".ppt", ".pptx"]):
        """
        Gets all the files in the root folder and its subfolders with the given extensions.

        Args:
            root_folder (str): The root folder to search for files.
            extensions (list): The extensions of the files to search for.

        Returns:
            List[str]: A list of file paths that match the given extensions.
        """
        matched_files = []
        for root, dirs, files in os.walk(root_folder):
            for file in files:
                if os.path.splitext(file)[1].lower() in extensions:
                    matched_files.append(os.path.join(root, file))
        return matched_files

    def _load_pdf_text(self, file_path):
        try:
            doc = fitz.open(file_path)
            return "\n".join(page.get_text() for page in doc)
        except Exception as e:
            return f"[PDF READ ERROR]: {e}"
    
    def _load_txt_text(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"[TEXT READ ERROR]: {e}"
    
    def _load_pptx_text(self, file_path):
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
