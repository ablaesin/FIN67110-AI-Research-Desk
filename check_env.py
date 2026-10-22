"""Read the local Session 1 environment file without exposing the full API key."""

from pathlib import Path


def load_dotenv(path: Path) -> dict[str, str]:
    """Read simple KEY=VALUE lines from a local .env file."""
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if not separator:
            raise ValueError(f"Invalid .env line: {raw_line!r}")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def main() -> None:
    env_path = Path(__file__).with_name(".env")
    if not env_path.exists():
        raise FileNotFoundError("Create a .env file next to check_env.py first.")

    values = load_dotenv(env_path)
    api_key = values.get("API_KEY", "")
    user_agent = values.get("SEC_USER_AGENT", "")

    print(f"{api_key[:4]}...")
    print(user_agent)


if __name__ == "__main__":
    main()
