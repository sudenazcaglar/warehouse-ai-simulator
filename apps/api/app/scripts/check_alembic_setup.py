from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


def main() -> None:
    alembic_ini = Path("alembic.ini")

    if not alembic_ini.exists():
        raise FileNotFoundError("alembic.ini was not found in the API container.")

    config = Config(str(alembic_ini))
    script = ScriptDirectory.from_config(config)

    heads = script.get_heads()

    print("Alembic configuration loaded successfully.")
    print(f"Revision heads: {heads if heads else 'no revisions yet'}")


if __name__ == "__main__":
    main()
