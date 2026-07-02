from app.api.deps import validate_uuid
from app.api.errors import BadRequestError, ConflictError, DatabaseOperationError, NotFoundError
from app.schemas.errors import ErrorDetail, ErrorResponse, ValidationErrorDetail
from app.schemas.pagination import PaginatedResponse, PaginationParams


def main() -> None:
    pagination = PaginationParams(page=2, page_size=25)

    if pagination.offset != 25:
        raise RuntimeError("Pagination offset calculation failed.")

    paginated_response = PaginatedResponse.create(
        items=[{"id": "demo"}],
        total=51,
        pagination=pagination,
    )

    if paginated_response.pages != 3:
        raise RuntimeError("Pagination page calculation failed.")

    error_response = ErrorResponse(
        error=ErrorDetail(
            code="not_found",
            message="Resource not found.",
            details={},
            request_id="demo-request-id",
        )
    )

    if error_response.error.code != "not_found":
        raise RuntimeError("Error response schema validation failed.")

    validation_error = ValidationErrorDetail(
        location=["query", "page"],
        message="Input should be greater than or equal to 1",
        error_type="greater_than_equal",
    )

    if validation_error.location != ["query", "page"]:
        raise RuntimeError("Validation error schema validation failed.")

    for error_class in [BadRequestError, NotFoundError, ConflictError, DatabaseOperationError]:
        error = error_class()

        if not error.code or not error.message or not error.status_code:
            raise RuntimeError(f"{error_class.__name__} is not configured correctly.")

    try:
        validate_uuid("not-a-valid-uuid", "run_id")
    except BadRequestError as exc:
        if exc.code != "invalid_uuid":
            raise RuntimeError("UUID validation did not raise the expected error code.")
    else:
        raise RuntimeError("UUID validation did not fail for an invalid UUID.")

    print("Common API error foundation verification successful.")
    print("- PaginationParams")
    print("- PaginatedResponse")
    print("- ErrorResponse")
    print("- ValidationErrorDetail")
    print("- APIError subclasses")
    print("- UUID validation helper")


if __name__ == "__main__":
    main()
