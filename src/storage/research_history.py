
import json
from pathlib import Path
from datetime import datetime, timezone


HISTORY_DIR = Path("data/research_history")
HISTORY_FILE = HISTORY_DIR / "history.json"


def load_research_history():
    """
    Load all previously saved research runs.
    """

    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            history = json.load(file)

        if isinstance(history, list):
            return history

        return []

    except (json.JSONDecodeError, OSError):
        return []


def save_research_history(result):
    """
    Save a completed research run.
    """

    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    history = load_research_history()

    history_id = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    record = {
        "id": history_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "topic": result.get("topic", ""),
        "summary": result.get("summary", ""),
        "analysis": result.get("analysis", ""),
        "literature_review": result.get("literature_review", ""),
        "research_gaps": result.get("research_gaps", ""),
        "chunks": result.get("chunks", []),
        "sources": result.get("sources", []),
        "metadata_results": result.get("metadata_results", []),
        "claim_verification": result.get("claim_verification", {}),
        "pdf_path": result.get("pdf_path", "")
    }

    history.insert(0, record)

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False, default=str)

    return history_id


def get_research_by_id(history_id):
    """
    Find one saved research run using its ID.
    """

    history = load_research_history()

    for record in history:
        if record.get("id") == history_id:
            return record

    return None
