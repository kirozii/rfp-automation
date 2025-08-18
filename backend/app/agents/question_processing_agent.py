import logging
from ..database import get_db
import asyncio
from typing import List
import pandas as pd
from sqlalchemy.orm import Session
from ..models import RFPStatus
from ..crud import rfps, questions

logger = logging.getLogger("rfpai.agents.question_processing_agent")

class QuestionProcessingAgent:
    """
    Agent which extracts questions from an RFP and saves them to the database.
    """
    db: Session

    def __init__(self, db: Session):
        """
        Initializes an instance of the agent.

        Args:
            db (Session): An SQLAlchemy database session
        """
        self.db = db
        logger.info("Question processing agent initialized.")

    async def process(self, rfp_id: int):
        """
        Extracts questions from an rfp.

        Args:
            rfp_id (int): The rfp_id of the document we need to extract questions from.
        """
        logger.info("Starting extraction of questions from rfp_id: %s", rfp_id)
        db_rfp = await asyncio.to_thread(rfps.get_rfp, self.db, rfp_id)
        if db_rfp is None:
            logger.error("Could not find rfp with rfp_id: %s", rfp_id)
            return
        filepath = db_rfp.storage_path
        question_list = self._read_excel(filepath)

        logger.info("Found %d questions for rfp_id: %d. Saving to database.", len(question_list), rfp_id)
        tasks = [asyncio.to_thread(self._create_question_threadsafe, rfp_id, question_text) for question_text in question_list]
        try:
            await asyncio.gather(*tasks)
            logger.info("Successfully saved all questions for rfp_id: %s", rfp_id)
        except Exception as e:
            logger.error("Failed to save questions for rfp_id %s: %s", rfp_id, e, exc_info=True)
            rfps.update_rfp_status(self.db, rfp_id, RFPStatus.FAILED)


    def _create_question_threadsafe(self, rfp_id: int, question_text: str):
        """
        Wrapper for questions.create_question so it is threadsafe.
        """
        db = next(get_db())
        try:
            questions.create_question(db, rfp_id, question_text)
        finally:
            db.close()

    def _read_excel(self, filepath: str) -> List[str]:
        """
        Extracts questions from an excel file.

        Args:
            filepath (str): Path of the excel file

        Returns:
            List[str]: A list of all the questions in the excel file.
        """
        # Note: ive kept this as a seperate method so we can extend for multiple filetypes with intelligent detection in the future, if the need arises
        try:
            questions_df = pd.read_excel(filepath, engine='openpyxl')
            cleaned_columns = [col.lower().replace(" ", "") for col in questions_df.columns]
            target_column_name = "questions"

            if target_column_name in cleaned_columns:
                original_column_index = cleaned_columns.index(target_column_name)
                original_column_name = questions_df.columns[original_column_index]

                questions_list = questions_df[original_column_name].dropna().tolist()
                return questions_list
            else:
                raise ValueError(f"Column '{target_column_name}' not found in the file.")

        except FileNotFoundError:
            raise FileNotFoundError(f"Error: The file at {filepath} was not found.")
        except Exception as e:
            logger.exception(f"An unexpected error occurred while processing file {filepath}: {e}")
            raise
