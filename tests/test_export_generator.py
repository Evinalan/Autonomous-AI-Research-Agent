
from src.exporting.export_generator import (
    export_research_json,
    export_research_markdown,
    create_export_filename
)

import json


def test_json_export():

    research = {
        "topic": "Deep Learning",
        "summary": "A test research summary.",
        "sources": []
    }

    result = export_research_json(research)

    parsed = json.loads(result)

    assert parsed["topic"] == "Deep Learning"
    assert parsed["summary"] == "A test research summary."


def test_markdown_export():

    research = {
        "topic": "Deep Learning",
        "summary": "A test research summary.",
        "literature_review": "A test literature review.",
        "analysis": "A test analysis.",
        "research_gaps": "A test research gap.",
        "sources": []
    }

    result = export_research_markdown(research)

    assert "# Deep Learning" in result
    assert "Research Summary" in result
    assert "A test research summary." in result
    assert "Research Gaps" in result


def test_export_filename():

    filename = create_export_filename(
        "Deep Learning Research",
        "json"
    )

    assert filename.endswith(".json")
    assert "Deep_Learning_Research" in filename
