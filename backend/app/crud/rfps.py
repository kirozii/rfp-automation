import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import exc
from typing import List, Optional

from .. import models
from ..models import RFPStatus

logger = logging.getLogger(__name__)


async def create_rfp(
    db: AsyncSession, filename: str, storage_path: Optional[str] = None
) -> models.RFP:
    """
    Creates a new RFP record in the database.

    Args:
        db (AsyncSession): The SQLAlchemy async database session.
        filename (str): The original filename of the uploaded RFP.
        storage_path (Optional[str]): The path where the RFP file is stored (e.g., cloud URL).

    Returns:
        models.RFP: The newly created RFP ORM object, with its ID populated.
    Raises:
        Exception: If there's a database error during creation.
    """
    db_rfp = models.RFP(
        filename=filename,
        storage_path=storage_path,
        status=RFPStatus.UPLOADED,
    )
    try:
        print(db)
        db.add(db_rfp)
        await db.commit()
        await db.refresh(db_rfp)
        logger.info(
            f"Created new RFP: ID={db_rfp.rfp_id}, Filename='{db_rfp.filename}'"
        )
        return db_rfp
    except exc.SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            f"Error creating RFP for filename '{filename}': {e}", exc_info=True
        )
        raise


async def get_rfp(db: AsyncSession, rfp_id: int) -> Optional[models.RFP]:
    """
    Retrieves an RFP record by its primary key ID.

    Args:
        db (AsyncSession): The SQLAlchemy async database session.
        rfp_id (int): The primary key ID of the RFP to retrieve.

    Returns:
        Optional[models.RFP]: The RFP ORM object if found, None otherwise.
    """
    result = await db.execute(select(models.RFP).filter(models.RFP.rfp_id == rfp_id))
    rfp = result.scalar_one_or_none()
    if rfp:
        logger.debug(f"Retrieved RFP: ID={rfp_id}, Filename='{rfp.filename}'")
    else:
        logger.warning(f"RFP with ID {rfp_id} not found.")
    return rfp


async def get_rfps(db: AsyncSession, skip: int = 0, limit: int = 5) -> List[models.RFP]:
    """
    Retrieves a list of RFP records. Retrieves a default of the 5 newest objects.

    Args:
        db (AsyncSession): The SQLAlchemy async database session.
        skip (int): The number of records to skip (offset).
        limit (int): The maximum number of records to return.

    Returns:
        List[models.RFP]: A list of RFP ORM objects.
    """
    result = await db.execute(
        select(models.RFP).order_by(models.RFP.rfp_id.desc()).offset(skip).limit(limit)
    )
    rfps = result.scalars().all()
    logger.debug(f"Retrieved {len(rfps)} RFPs (skip={skip}, limit={limit}).")
    return rfps


async def update_rfp_status(
    db: AsyncSession, rfp_id: int, new_status: RFPStatus
) -> Optional[models.RFP]:
    """
    Updates the status of an RFP record.

    Args:
        db (AsyncSession): The SQLAlchemy async database session.
        rfp_id (int): The ID of the RFP to update.
        new_status (RFPStatus): The new status for the RFP.

    Returns:
        Optional[models.RFP]: The updated RFP ORM object if found, None otherwise.
    Raises:
        ValueError: If the RFP with the given ID is not found.
        Exception: If there's a database error during the update.
    """
    db_rfp = await get_rfp(db, rfp_id)
    if db_rfp:
        old_status = db_rfp.status
        db_rfp.status = new_status
        try:
            await db.commit()
            await db.refresh(db_rfp)
            logger.info(
                f"Updated RFP ID={rfp_id} status from '{old_status.value}' to '{new_status.value}'"
            )
            return db_rfp
        except exc.SQLAlchemyError as e:
            await db.rollback()
            logger.error(
                f"Error updating RFP ID={rfp_id} status to '{new_status.value}': {e}",
                exc_info=True,
            )
            raise
    else:
        logger.warning(f"Attempted to update status for non-existent RFP ID={rfp_id}")
        raise ValueError(f"RFP with ID {rfp_id} not found for status update.")


async def update_storage_path(
    db: AsyncSession, rfp_id: int, new_storage_path: Optional[str]
) -> Optional[models.RFP]:
    """
    Updates the storage path of an RFP record.

    Args:
        db (AsyncSession): The SQLAlchemy async database session.
        rfp_id (int): The ID of the RFP to update.
        new_storage_path (Optional[str]): The new storage path (e.g., cloud URL).

    Returns:
        Optional[models.RFP]: The updated RFP ORM object if found, None otherwise.
    Raises:
        ValueError: If the RFP with the given ID is not found.
        Exception: If there's a database error during the update.
    """
    db_rfp = await get_rfp(db, rfp_id)
    if db_rfp:
        old_path = db_rfp.storage_path
        db_rfp.storage_path = new_storage_path
        try:
            await db.commit()
            await db.refresh(db_rfp)
            logger.info(
                f"Updated RFP ID={rfp_id} storage_path from '{old_path}' to '{new_storage_path}'"
            )
            return db_rfp
        except exc.SQLAlchemyError as e:
            await db.rollback()
            logger.error(
                f"Error updating RFP ID={rfp_id} storage_path to '{new_storage_path}': {e}",
                exc_info=True,
            )
            raise
    else:
        logger.warning(
            f"Attempted to update storage_path for non-existent RFP ID={rfp_id}"
        )
        raise ValueError(f"RFP with ID {rfp_id} not found for storage_path update.")


async def delete_rfp(db: AsyncSession, rfp_id: int) -> bool:
    """
    Deletes an RFP record by its ID.
    Note: Deleting an RFP will typically cascade delete related questions,
    LLM responses, evaluations, and presentations due to foreign key constraints
    with CASCADE ON DELETE defined in the database (which SQLAlchemy doesn't set
    by default but you can configure or handle manually).

    Args:
        db (AsyncSession): The SQLAlchemy async database session.
        rfp_id (int): The ID of the RFP to delete.

    Returns:
        bool: True if the RFP was deleted, False otherwise (e.g., not found).
    Raises:
        Exception: If there's a database error during deletion.
    """
    db_rfp = await get_rfp(db, rfp_id)
    if db_rfp:
        try:
            await db.delete(db_rfp)
            await db.commit()
            logger.info(f"Deleted RFP ID={rfp_id}")
            return True
        except exc.SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Error deleting RFP ID={rfp_id}: {e}", exc_info=True)
            raise
    else:
        logger.warning(f"Attempted to delete non-existent RFP ID={rfp_id}")
        return False
