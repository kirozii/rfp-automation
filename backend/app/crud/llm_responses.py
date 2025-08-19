from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exc
import logging

from .. import models

logger = logging.getLogger(__name__)


async def create_llm_response(
    db: AsyncSession,
    question_id: int,
    response: str,
    model_id: Optional[str] = None,
    retrieved_context: Optional[str] = None,
    retrieval_time_ms: Optional[int] = None,
    generation_time_ms: Optional[int] = None,
    tokens_used: Optional[int] = None,
    status: str = "initial_draft",  # Can be an Enum later if more defined states are needed but i kept it simple for now
) -> models.LLMResponse:
    """
    Creates a new LLMResponse record in the database, linked to a Question.

    Args:
        db (Session): The SQLAlchemy database session.
        question_id (int): The ID of the parent Question.
        response (str): The actual text response from the LLM.
        model_id (Optional[str]): Identifier for the LLM model used.
        retrieved_context (Optional[str]): The context used for this specific LLM call.
        retrieval_time_ms (Optional[int]): Time taken for context retrieval.
        generation_time_ms (Optional[int]): Time taken for LLM generation.
        tokens_used (Optional[int]): Number of tokens consumed.
        status (str): Status of the LLM response (e.g., "initial_draft", "refined").

    Returns:
        models.LLMResponse: The newly created LLMResponse ORM object, with its ID populated.
    Raises:
        Exception: If there's a database error during creation.
    """
    db_llm_response = models.LLMResponse(
        question_id=question_id,
        response=response,
        model_id=model_id,
        retrieved_context=retrieved_context,
        retrieval_time_ms=retrieval_time_ms,
        generation_time_ms=generation_time_ms,
        tokens_used=tokens_used,
        status=status,
    )
    try:
        db.add(db_llm_response)
        await db.commit()
        await db.refresh(db_llm_response)
        logger.info(
            f"Created new LLMResponse: ID={db_llm_response.response_id} "
            f"for Question ID={question_id}"
        )
        return db_llm_response
    except exc.SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            f"Error creating LLMResponse for Question ID '{question_id}': {e}",
            exc_info=True,
        )
        raise


async def get_llm_response(
    db: AsyncSession, response_id: int
) -> Optional[models.LLMResponse]:
    """
    Retrieves an LLMResponse record by its primary key ID.

    Args:
        db (Session): The SQLAlchemy database session.
        response_id (int): The ID of the LLM response to retrieve.

    Returns:
        Optional[models.LLMResponse]: The LLMResponse ORM object if found, None otherwise.
    """
    result = await db.execute(
        select(models.LLMResponse).where(models.LLMResponse.response_id == response_id)
    )
    llm_response = result.scalar_one_or_none()
    if llm_response:
        logger.debug(
            f"Retrieved LLMResponse: ID={response_id}, Model='{llm_response.model_id}'"
        )
    else:
        logger.warning(f"LLMResponse with ID {response_id} not found.")
    return llm_response


async def get_llm_responses_by_question(
    db: AsyncSession, question_id: int
) -> models.LLMResponse:
    """
    Retrieves the LLM response associated with a specific Question.

    Args:
        db (Session): The SQLAlchemy database session.
        question_id (int): The ID of the parent Question.

    Returns:
        List[models.LLMResponse]: A list of LLMResponse ORM objects.
    """
    result = await db.execute(
        select(models.LLMResponse).where(models.LLMResponse.question_id == question_id)
    )
    llm_responses = result.scalars().first()
    logger.debug(f"Retrieved LLM response for Question ID={question_id}.")
    return llm_responses


async def update_llm_response(
    db: AsyncSession,
    response_id: int,
    response_text: Optional[str] = None,
    status: Optional[str] = None,
) -> Optional[models.LLMResponse]:
    """
    Updates fields of an LLMResponse record.

    Args:
        db (Session): The SQLAlchemy database session.
        response_id (int): The ID of the LLMResponse to update.
        response_text (Optional[str]): New response text.
        status (Optional[str]): New status for the LLM response.

    Returns:
        Optional[models.LLMResponse]: The updated LLMResponse ORM object if found, None otherwise.
    Raises:
        ValueError: If the LLMResponse is not found.
        Exception: If there's a database error during the update.
    """
    db_llm_response = await get_llm_response(db, response_id)
    if db_llm_response:
        if response_text is not None:
            db_llm_response.response = response_text
        if status is not None:
            db_llm_response.status = status

        try:
            await db.commit()
            await db.refresh(db_llm_response)
            logger.info(f"Updated LLMResponse ID={response_id}.")
            return db_llm_response
        except exc.SQLAlchemyError as e:
            await db.rollback()
            logger.error(
                f"Error updating LLMResponse ID={response_id}: {e}", exc_info=True
            )
            raise
    else:
        logger.warning(f"Attempted to update non-existent LLMResponse ID={response_id}")
        raise ValueError(f"LLMResponse with ID {response_id} not found for update.")


async def delete_llm_response(db: AsyncSession, response_id: int) -> bool:
    """
    Deletes an LLMResponse record by its ID.
    Note: Deleting an LLMResponse will typically cascade delete related evaluations.

    Args:
        db (Session): The SQLAlchemy database session.
        response_id (int): The ID of the LLMResponse to delete.

    Returns:
        bool: True if the LLM response was deleted, False otherwise (e.g., not found).
    Raises:
        Exception: If there's a database error during deletion.
    """
    db_llm_response = await get_llm_response(db, response_id)
    if db_llm_response:
        try:
            await db.delete(db_llm_response)
            await db.commit()
            logger.info(f"Deleted LLMResponse ID={response_id}")
            return True
        except exc.SQLAlchemyError as e:
            await db.rollback()
            logger.error(
                f"Error deleting LLMResponse ID={response_id}: {e}", exc_info=True
            )
            raise
    else:
        logger.warning(f"Attempted to delete non-existent LLMResponse ID={response_id}")
        return False
