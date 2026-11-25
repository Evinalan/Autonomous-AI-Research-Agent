
import json
from pathlib import Path


# Locate the main project directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Location where collected papers will be saved.
DATA_FOLDER = PROJECT_ROOT / "data" / "processed"

PAPER_FILE = DATA_FOLDER / "research_papers.json"


def save_papers(papers):

    try:

        DATA_FOLDER.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            PAPER_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                papers,
                file,
                indent=4,
                ensure_ascii=False
            )

        print("\nResearch papers saved successfully!")

        print("File location:", PAPER_FILE)

        return True

    except (OSError, TypeError, ValueError) as error:

        print("Error saving research papers:", error)

        return False


def load_papers():

    try:

        if not PAPER_FILE.exists():
            return []

        with open(
            PAPER_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            papers = json.load(file)

        return papers

    except (OSError, json.JSONDecodeError) as error:

        print("Error loading research papers:", error)

        return []
