from pathlib import Path
from functools import lru_cache

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"

@lru_cache(maxsize=None)
def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8").strip()
