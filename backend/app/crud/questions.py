from typing import Any, Dict, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError as exc
import logging

from .. import models
from ..models import QuestionStatus

logger = logging.getLogger(__name__)


async def create_question(
    db: AsyncSession,
    rfp_id: int,
    question_text: str,
    question_context: Optional[str] = None,
    page_number: Optional[int] = None,
) -> models.Question:
    """
    Creates a new Question record in the database, linked to an RFP.

    Args:
        db (Session): The SQLAlchemy database session.
        rfp_id (int): The ID of the parent RFP.
        question_text (str): The actual text of the question.
        question_context (Optional[str]): Retrieved context for the question.
        page_number (Optional[int]): The page number in the original RFP.

    Returns:
        models.Question: The newly created Question ORM object, with its ID populated.
    Raises:
        Exception: If there's a database error during creation.
    """
    db_question = models.Question(
        rfp_id=rfp_id,
        question_text=question_text,
        question_context=question_context,
        page_number=page_number,
        status=QuestionStatus.EXTRACTED,
    )
    try:
        db.add(db_question)
        await db.commit()
        await db.refresh(db_question)
        logger.info(
            f"Created new Question: ID={db_question.question_id} for RFP ID={rfp_id}"
        )
        return db_question
    except exc as e:
        await db.rollback()
        logger.error(
            f"Error creating question for RFP ID '{rfp_id}': {e}", exc_info=True
        )
        raise


async def get_question(db: AsyncSession, question_id: int) -> Optional[models.Question]:
    """
    Retrieves a Question record by its primary key ID.

    Args:
        db (Session): The SQLAlchemy database session.
        question_id (int): The ID of the question to retrieve.

    Returns:
        Optional[models.Question]: The Question ORM object if found, None otherwise.
    """
    stmt = select(models.Question).filter(models.Question.question_id == question_id)
    result = await db.execute(stmt)
    question = result.scalars().first()

    if question:
        logger.debug(
            f"Retrieved Question: ID={question_id}, Text='{question.question_text[:50]}...'"
        )
    else:
        logger.warning(f"Question with ID {question_id} not found.")

    return question


async def get_questions_by_rfp(db: AsyncSession, rfp_id: int) -> List[models.Question]:
    """
    Retrieves all questions associated with a specific RFP.
    """
    stmt = select(models.Question).filter(models.Question.rfp_id == rfp_id)
    result = await db.execute(stmt)
    questions = result.scalars().all()
    logger.debug(f"Retrieved {len(questions)} questions for RFP ID={rfp_id}.")
    return questions


async def update_question_context(
    db: AsyncSession, question_id: int, new_context: str
) -> Optional[models.Question]:
    """
    Updates the question_context of a Question record.

    Args:
        db (AsyncSession): The SQLAlchemy database session.
        question_id (int): The ID of the question to update.
        new_context (str): The new context to set for the question.

    Returns:
        Optional[models.Question]: The updated Question ORM object if found, None otherwise.

    Raises:
        ValueError: If the question with the given ID is not found.
        Exception: If there's a database error during the update.
    """
    db_question = await get_question(db, question_id)
    if not db_question:
        logger.warning(
            f"Attempted to update context for non-existent Question ID={question_id}"
        )
        raise ValueError(
            f"Question with ID {question_id} not found for context update."
        )

    old_context = db_question.question_context
    db_question.question_context = new_context

    try:
        await db.commit()
        await db.refresh(db_question)
        logger.info(
            f"Updated Question ID={question_id} context from "
            f"'{old_context[:50]}...' to '{new_context[:50]}...'"
        )
        return db_question
    except exc as e:
        await db.rollback()
        logger.error(
            f"Error updating Question ID={question_id} context: {e}",
            exc_info=True,
        )
        raise


async def update_question_status(
    db: AsyncSession, question_id: int, new_status: QuestionStatus
) -> Optional[models.Question]:
    """
    Updates the status of a Question record.
    """
    db_question = await get_question(db, question_id)
    if db_question:
        old_status = db_question.status
        db_question.status = new_status
        try:
            await db.commit()
            await db.refresh(db_question)
            logger.info(
                f"Updated Question ID={question_id} status from '{old_status.value}' to '{new_status.value}'"
            )
            return db_question
        except exc as e:
            await db.rollback()
            logger.error(
                f"Error updating Question ID={question_id} status to '{new_status.value}': {e}",
                exc_info=True,
            )
            raise
    else:
        logger.warning(
            f"Attempted to update status for non-existent Question ID={question_id}"
        )
        raise ValueError(f"Question with ID {question_id} not found for status update.")


async def delete_question(db: AsyncSession, question_id: int) -> bool:
    """
    Deletes a Question record by its ID.
    """
    db_question = await get_question(db, question_id)
    if db_question:
        try:
            await db.delete(db_question)
            await db.commit()
            logger.info(f"Deleted Question ID={question_id}")
            return True
        except exc as e:
            await db.rollback()
            logger.error(
                f"Error deleting Question ID={question_id}: {e}", exc_info=True
            )
            raise
    else:
        logger.warning(f"Attempted to delete non-existent Question ID={question_id}")
        return False
