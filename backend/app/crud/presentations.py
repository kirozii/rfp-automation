from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exc
import logging

from .. import models

logger = logging.getLogger(__name__)


async def create_presentation(
    db: AsyncSession,
    rfp_id: int,
    filename: str,
    storage_path: str,
    generation_time_s: Optional[int] = None,
) -> models.Presentation:
    """
    Creates a new Presentation record in the database, linked to an RFP.

    Args:
        db (Session): The SQLAlchemy database session.
        rfp_id (int): The ID of the parent RFP.
        filename (str): The name of the generated presentation file.
        storage_path (str): The path where the presentation file is stored.
        generation_time_s (Optional[int]): Time taken to generate the presentation in seconds.

    Returns:
        models.Presentation: The newly created Presentation ORM object, with its ID populated.
    Raises:
        Exception: If there's a database error during creation.
    """
    db_presentation = models.Presentation(
        rfp_id=rfp_id,
        filename=filename,
        storage_path=storage_path,
        generation_time_s=generation_time_s,
    )
    try:
        db.add(db_presentation)
        await db.commit()
        await db.refresh(db_presentation)
        logger.info(
            f"Created new Presentation: ID={db_presentation.presentation_id} for RFP ID={rfp_id}"
        )
        return db_presentation
    except exc.SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            f"Error creating Presentation for RFP ID '{rfp_id}': {e}", exc_info=True
        )
        raise


async def get_presentation(
    db: AsyncSession, presentation_id: int
) -> Optional[models.Presentation]:
    """
    Retrieves a Presentation record by its primary key ID.

    Args:
        db (Session): The SQLAlchemy database session.
        presentation_id (int): The ID of the presentation to retrieve.

    Returns:
        Optional[models.Presentation]: The Presentation ORM object if found, None otherwise.
    """
    result = await db.execute(
        select(models.Presentation).where(
            models.Presentation.presentation_id == presentation_id
        )
    )
    presentation = result.scalar_one_or_none()
    if presentation:
        logger.debug(
            f"Retrieved Presentation: ID={presentation_id}, Filename='{presentation.filename}'"
        )
    else:
        logger.warning(f"Presentation with ID {presentation_id} not found.")
    return presentation


async def get_presentations_by_rfp(
    db: AsyncSession, rfp_id: int
) -> List[models.Presentation]:
    """
    Retrieves all presentations associated with a specific RFP.

    Args:
        db (Session): The SQLAlchemy database session.
        rfp_id (int): The ID of the parent RFP.

    Returns:
        List[models.Presentation]: A list of Presentation ORM objects.
    """
    result = await db.execute(
        select(models.Presentation).where(models.Presentation.rfp_id == rfp_id)
    )
    presentations = result.scalars().all()
    logger.debug(f"Retrieved {len(presentations)} presentations for RFP ID={rfp_id}.")
    return presentations


async def update_presentation(
    db: AsyncSession,
    presentation_id: int,
    filename: Optional[str] = None,
    storage_path: Optional[str] = None,
    generation_time_s: Optional[int] = None,
) -> Optional[models.Presentation]:
    """
    Updates fields of a Presentation record.

    Args:
        db (Session): The SQLAlchemy database session.
        presentation_id (int): The ID of the Presentation to update.
        filename (Optional[str]): New filename for the presentation.
        storage_path (Optional[str]): New storage path for the presentation.
        generation_time_s (Optional[int]): New generation time.

    Returns:
        Optional[models.Presentation]: The updated Presentation ORM object if found, None otherwise.
    Raises:
        ValueError: If the Presentation is not found.
        Exception: If there's a database error during the update.
    """
    db_presentation = await get_presentation(db, presentation_id)
    if db_presentation:
        if filename is not None:
            db_presentation.filename = filename
        if storage_path is not None:
            db_presentation.storage_path = storage_path
        if generation_time_s is not None:
            db_presentation.generation_time_s = generation_time_s

        try:
            await db.commit()
            await db.refresh(db_presentation)
            logger.info(f"Updated Presentation ID={presentation_id}.")
            return db_presentation
        except exc.SQLAlchemyError as e:
            await db.rollback()
            logger.error(
                f"Error updating Presentation ID={presentation_id}: {e}", exc_info=True
            )
            raise
    else:
        logger.warning(
            f"Attempted to update non-existent Presentation ID={presentation_id}"
        )
        raise ValueError(
            f"Presentation with ID {presentation_id} not found for update."
        )


async def delete_presentation(db: AsyncSession, presentation_id: int) -> bool:
    """
    Deletes a Presentation record by its ID.

    Args:
        db (Session): The SQLAlchemy database session.
        presentation_id (int): The ID of the presentation to delete.

    Returns:
        bool: True if the presentation was deleted, False otherwise (e.g., not found).
    Raises:
        Exception: If there's a database error during deletion.
    """
    db_presentation = await get_presentation(db, presentation_id)
    if db_presentation:
        try:
            await db.delete(db_presentation)
            await db.commit()
            logger.info(f"Deleted Presentation ID={presentation_id}")
            return True
        except exc.SQLAlchemyError as e:
            await db.rollback()
            logger.error(
                f"Error deleting Presentation ID={presentation_id}: {e}", exc_info=True
            )
            raise
    else:
        logger.warning(
            f"Attempted to delete non-existent Presentation ID={presentation_id}"
        )
        return False
