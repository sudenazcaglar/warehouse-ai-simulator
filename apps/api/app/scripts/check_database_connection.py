from app.db.session import check_database_connection


def main() -> None:
    result = check_database_connection()

    if result != 1:
        raise RuntimeError("Database connection check failed.")

    print("Database connection successful. SELECT 1 returned 1.")


if __name__ == "__main__":
    main()
