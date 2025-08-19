import logging
from ..database import async_session_factory
from typing import List
import pandas as pd
from ..models import RFPStatus
from ..crud import rfps, questions

logger = logging.getLogger("rfpai.agents.question_processing_agent")


class QuestionProcessingAgent:
    """
    Agent which extracts questions from an RFP and saves them to the database.
    """

    def __init__(self):
        """
        Initializes an instance of the agent.

        No purpose yet. Could add functionality if/when queues are used for each agent.
        """
        logger.info("Question processing agent initialized.")

    async def process(self, rfp_id: int):
        """
        Extracts questions from an rfp.

        Args:
            rfp_id (int): The rfp_id of the document we need to extract questions from.
        """
        logger.info("Starting extraction of questions from rfp_id: %s", rfp_id)
        async with async_session_factory() as session:
            db_rfp = await rfps.get_rfp(session, rfp_id)
            if db_rfp is None:
                logger.error("Could not find rfp with rfp_id: %s", rfp_id)
                return
            filepath = db_rfp.storage_path
            question_list = self._read_excel(filepath)

            logger.info(
                "Found %d questions for rfp_id: %d. Saving to database.",
                len(question_list),
                rfp_id,
            )
            existing_questions = await questions.get_questions_by_rfp(session, rfp_id)
            if existing_questions:
                logger.info(
                    "Skipping extraction: %d questions already exist for rfp_id: %s",
                    len(existing_questions),
                    rfp_id,
                )
                return

            try:
                for question in question_list:
                    await questions.create_question(session, rfp_id, question)
                    logger.info(
                        "Successfully extracted question with text: %s", question
                    )
            except Exception as e:
                logger.error(
                    "Failed to save questions for rfp_id %s: %s",
                    rfp_id,
                    e,
                    exc_info=True,
                )
                await rfps.update_rfp_status(session, rfp_id, RFPStatus.FAILED)

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
            questions_df = pd.read_excel(filepath, engine="openpyxl")
            cleaned_columns = [
                col.lower().replace(" ", "") for col in questions_df.columns
            ]
            target_column_name = "questions"

            if target_column_name in cleaned_columns:
                original_column_index = cleaned_columns.index(target_column_name)
                original_column_name = questions_df.columns[original_column_index]

                questions_list = questions_df[original_column_name].dropna().tolist()
                return questions_list
            else:
                raise ValueError(
                    f"Column '{target_column_name}' not found in the file."
                )

        except FileNotFoundError:
            raise FileNotFoundError(f"Error: The file at {filepath} was not found.")
        except Exception as e:
            logger.exception(
                f"An unexpected error occurred while processing file {filepath}: {e}"
            )
            raise
