"""Environment variable loader for Pastry Shop.

Automatically loads environment variables from a .env file located at the
project root (for local development).

Crucially, existing environment variables (such as those provided in Render,
Docker, CI/CD, or by the system shell) are NEVER overwritten (override=False).
This guarantees that deployment configurations take precedence over local file
defaults.
"""

from __future__ import annotations

import os
from pathlib import Path


def load_env(env_path: Path | str | None = None) -> None:
    """Load environment variables from a .env file if it exists.

    Variables already set in os.environ are NEVER overwritten, ensuring that
    deployment configurations (such as in Render and Docker) always take precedence.

    Args:
        env_path: Path to the .env file. Defaults to BASE_DIR / ".env"
                  (the project root).
    """
    if env_path is None:
        base_dir = Path(__file__).resolve().parent.parent
        env_path = base_dir / ".env"
    else:
        env_path = Path(env_path)

    if not env_path.is_file():
        return

    try:
        from dotenv import load_dotenv

        load_dotenv(dotenv_path=env_path, override=False)
        return
    except ImportError:
        pass

    # Built-in fallback parser if python-dotenv is not installed
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[7:].strip()
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()
                # Strip matching surrounding quotes if present
                if len(val) >= 2 and (
                    (val.startswith('"') and val.endswith('"'))
                    or (val.startswith("'") and val.endswith("'"))
                ):
                    val = val[1:-1]
                if key and key not in os.environ:
                    os.environ[key] = val
    except OSError:
        pass
