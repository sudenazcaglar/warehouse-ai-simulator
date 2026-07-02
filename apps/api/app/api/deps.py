import logging
from collections.abc import Generator
from uuid import UUID

from fastapi import Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.errors import BadRequestError, DatabaseOperationError
from app.db.session import SessionLocal
from app.schemas.pagination import PaginationParams

logger = logging.getLogger("warehouse_api.dependencies")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("database_session_error error=%s", exc.__class__.__name__)
        raise DatabaseOperationError() from exc
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_pagination(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)


def validate_uuid(value: str | UUID, field_name: str = "id") -> UUID:
    if isinstance(value, UUID):
        return value

    try:
        return UUID(str(value))
    except ValueError as exc:
        raise BadRequestError(
            message=f"Invalid UUID value for '{field_name}'.",
            code="invalid_uuid",
            details={
                "field": field_name,
                "value": str(value),
            },
        ) from exc
