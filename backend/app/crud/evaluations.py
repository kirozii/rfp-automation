from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exc
import logging

from .. import models

logger = logging.getLogger(__name__)


async def create_evaluation(
    db: AsyncSession,
    response_id: int,
    original_response: Optional[str] = None,
    fine_tuned_response: Optional[str] = None,
    score: Optional[int] = None,
    sme_comments: Optional[str] = None,
) -> models.Evaluation:
    """
    Creates a new Evaluation record in the database, linked to an LLMResponse.

    Args:
        db (Session): The SQLAlchemy database session.
        response_id (int): The ID of the parent LLMResponse.
        original_response (Optional[str]): The original LLM generated response text.
        fine_tuned_response (Optional[str]): The human-tuned response text.
        score (Optional[int]): Numerical score given by the SME.
        sme_comments (Optional[str]): Textual comments from the SME.

    Returns:
        models.Evaluation: The newly created Evaluation ORM object, with its ID populated.
    Raises:
        Exception: If there's a database error during creation.
    """
    db_evaluation = models.Evaluation(
        response_id=response_id,
        original_response=original_response,
        fine_tuned_response=fine_tuned_response,
        score=score,
        sme_comments=sme_comments,
    )
    try:
        db.add(db_evaluation)
        await db.commit()
        await db.refresh(db_evaluation)
        logger.info(
            f"Created new Evaluation: ID={db_evaluation.id} for LLMResponse ID={response_id}"
        )
        return db_evaluation
    except exc.SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            f"Error creating Evaluation for LLMResponse ID '{response_id}': {e}",
            exc_info=True,
        )
        raise


async def get_evaluation(
    db: AsyncSession, evaluation_id: int
) -> Optional[models.Evaluation]:
    """
    Retrieves an Evaluation record by its primary key ID.

    Args:
        db (Session): The SQLAlchemy database session.
        evaluation_id (int): The ID of the evaluation to retrieve.

    Returns:
        Optional[models.Evaluation]: The Evaluation ORM object if found, None otherwise.
    """
    result = await db.execute(
        select(models.Evaluation).where(models.Evaluation.id == evaluation_id)
    )
    evaluation = result.scalar_one_or_none()
    if evaluation:
        logger.debug(
            f"Retrieved Evaluation: ID={evaluation_id}, Score={evaluation.score}"
        )
    else:
        logger.warning(f"Evaluation with ID {evaluation_id} not found.")
    return evaluation


async def get_evaluations_by_response(
    db: AsyncSession, response_id: int
) -> List[models.Evaluation]:
    """
    Retrieves all evaluations associated with a specific LLM Response.

    Args:
        db (Session): The SQLAlchemy database session.
        response_id (int): The ID of the parent LLM Response.

    Returns:
        List[models.Evaluation]: A list of Evaluation ORM objects.
    """
    result = await db.execute(
        select(models.Evaluation).where(models.Evaluation.response_id == response_id)
    )
    evaluations = result.scalars().all()
    logger.debug(
        f"Retrieved {len(evaluations)} evaluations for LLMResponse ID={response_id}."
    )
    return evaluations


async def update_evaluation(
    db: AsyncSession,
    evaluation_id: int,
    original_response: Optional[str] = None,
    fine_tuned_response: Optional[str] = None,
    score: Optional[int] = None,
    sme_comments: Optional[str] = None,
) -> Optional[models.Evaluation]:
    """
    Updates fields of an Evaluation record.

    Args:
        db (Session): The SQLAlchemy database session.
        evaluation_id (int): The ID of the Evaluation to update.
        original_response (Optional[str]): New original response text.
        fine_tuned_response (Optional[str]): New human-tuned response text.
        score (Optional[int]): New numerical score.
        sme_comments (Optional[str]): New textual comments.

    Returns:
        Optional[models.Evaluation]: The updated Evaluation ORM object if found, None otherwise.
    Raises:
        ValueError: If the Evaluation is not found.
        Exception: If there's a database error during the update.
    """
    db_evaluation = await get_evaluation(db, evaluation_id)
    if db_evaluation:
        if original_response is not None:
            db_evaluation.original_response = original_response
        if fine_tuned_response is not None:
            db_evaluation.fine_tuned_response = fine_tuned_response
        if score is not None:
            db_evaluation.score = score
        if sme_comments is not None:
            db_evaluation.sme_comments = sme_comments

        try:
            await db.commit()
            await db.refresh(db_evaluation)
            logger.info(f"Updated Evaluation ID={evaluation_id}.")
            return db_evaluation
        except exc.SQLAlchemyError as e:
            await db.rollback()
            logger.error(
                f"Error updating Evaluation ID={evaluation_id}: {e}", exc_info=True
            )
            raise
    else:
        logger.warning(
            f"Attempted to update non-existent Evaluation ID={evaluation_id}"
        )
        raise ValueError(f"Evaluation with ID {evaluation_id} not found for update.")


async def delete_evaluation(db: AsyncSession, evaluation_id: int) -> bool:
    """
    Deletes an Evaluation record by its ID.

    Args:
        db (Session): The SQLAlchemy database session.
        evaluation_id (int): The ID of the evaluation to delete.

    Returns:
        bool: True if the evaluation was deleted, False otherwise (e.g., not found).
    Raises:
        Exception: If there's a database error during deletion.
    """
    db_evaluation = await get_evaluation(db, evaluation_id)
    if db_evaluation:
        try:
            await db.delete(db_evaluation)
            await db.commit()
            logger.info(f"Deleted Evaluation ID={evaluation_id}")
            return True
        except exc.SQLAlchemyError as e:
            await db.rollback()
            logger.error(
                f"Error deleting Evaluation ID={evaluation_id}: {e}", exc_info=True
            )
            raise
    else:
        logger.warning(
            f"Attempted to delete non-existent Evaluation ID={evaluation_id}"
        )
        return False
