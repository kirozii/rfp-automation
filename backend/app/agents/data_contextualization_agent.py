from sqlalchemy.orm import Session
from ..core.config import settings
from pydantic import SecretStr
import logging
from openai import AsyncAzureOpenAI
from ..models import QuestionStatus
from ..crud import questions, llm_response

logger = logging.getLogger("rfpai.agents.data_contextualization_agent")

class DataContextualizationAgent:
    """
    Contextualizes and forms an answer to the provided question. 
    """
    _db: Session

    def __init__(self, db: Session):
        """
        Initializes an instance of the agent.

        Args:
            db (Session): An SQLAlchemy database session
        """
        self._db = db
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
        logger.info("Data Contextualization agent initialized.")

    async def process(self, question_id: int):
        """
        Contextualizes and forms an answer to the question provided.
        """
        logger.info("Starting data contextualization for question_id: %s", question_id)
        question = questions.get_question(self._db, question_id)
        if question is None:
            logger.error("Could not find question with question_id: %s", question_id)
            return
        questions.update_question_status(self._db, question_id, QuestionStatus.PENDING_LLM_RESPONSE)
        response = await self.rewrite_with_mphasis(question.question_text, question.question_context)
        db_response = llm_response.create_llm_response(self._db, question_id, response, model_id=self._model, retrieved_context=question.question_context)
        logger.info("Data contextualization completed for question_id: %s with llm_response id: %s", question_id, db_response.response_id)

    async def rewrite_with_mphasis(self, question, answer):
        prompt = f"""
        Contextualize the answer and make sure there is no markdown, and a maximum of 5 un-numbered points with 3 lines each are present. If the question is like "Your way of xyz", or "How would you handle it" rewrite it to sound like Mphasis is writing it. Do not use it for definitions etc, make sure the answer is contextualized and makes sense with the question.
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
