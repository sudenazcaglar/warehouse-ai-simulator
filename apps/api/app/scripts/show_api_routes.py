from app.main import app


def main() -> None:
    print("Registered API routes:")

    for route in sorted(app.routes, key=lambda item: getattr(item, "path", "")):
        path = getattr(route, "path", "")
        methods = sorted(getattr(route, "methods", []) or [])

        if not path:
            continue

        print(f"- {','.join(methods) or 'WS'} {path}")


if __name__ == "__main__":
    main()
