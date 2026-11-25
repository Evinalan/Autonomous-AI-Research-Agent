
import json
import re
from datetime import datetime, timezone


def export_research_json(result):
    """
    Convert research results into formatted JSON.
    """

    return json.dumps(
        result,
        indent=4,
        ensure_ascii=False,
        default=str
    )


def export_research_markdown(result):
    """
    Convert research results into a readable Markdown document.
    """

    topic = result.get("topic", "Untitled Research")

    summary = result.get("summary", "")
    literature_review = result.get("literature_review", "")
    analysis = result.get("analysis", "")
    research_gaps = result.get("research_gaps", "")

    lines = []

    lines.append(f"# {topic}")
    lines.append("")
    lines.append("## Research Report")
    lines.append("")

    lines.append(
        f"**Generated:** "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
    )

    lines.append("")
    lines.append("---")
    lines.append("")

    # RESEARCH SUMMARY

    lines.append("## Research Summary")
    lines.append("")
    lines.append(summary or "No summary available.")
    lines.append("")

    # LITERATURE REVIEW

    lines.append("## Literature Review")
    lines.append("")
    lines.append(
        literature_review or "No literature review available."
    )
    lines.append("")

    # RESEARCH ANALYSIS

    lines.append("## Research Analysis")
    lines.append("")
    lines.append(analysis or "No research analysis available.")
    lines.append("")

    # RESEARCH GAPS

    lines.append("## Research Gaps")
    lines.append("")
    lines.append(
        research_gaps or "No research gaps available."
    )
    lines.append("")

    # RESEARCH SOURCES

    lines.append("## Research Sources")
    lines.append("")

    sources = result.get("sources", [])

    if sources:

        for index, source in enumerate(sources, start=1):

            title = source.get("title", "Unknown title")
            authors = source.get("authors", "Unknown")
            year = (
                source.get("year")
                or source.get("published")
                or "Unknown"
            )

            if isinstance(authors, list):
                authors = ", ".join(str(author) for author in authors)

            lines.append(f"### {index}. {title}")
            lines.append("")
            lines.append(f"- **Authors:** {authors}")
            lines.append(f"- **Year:** {year}")
            lines.append(
                f"- **Database:** {source.get('source', 'Unknown')}"
            )
            lines.append(
                f"- **DOI:** {source.get('doi') or 'Not available'}"
            )

            paper_url = source.get("paper_url", "")

            if paper_url.startswith(("https://", "http://")):
                lines.append(f"- **Paper URL:** {paper_url}")

            lines.append("")

    else:

        lines.append("No research sources available.")
        lines.append("")

    # METADATA VERIFICATION

    lines.append("## Metadata Verification")
    lines.append("")

    metadata_results = result.get("metadata_results", [])

    if metadata_results:

        for index, item in enumerate(metadata_results, start=1):

            source = item.get("source", {})
            verification = item.get("result", {})

            lines.append(
                f"### Source {index}: "
                f"{source.get('title', 'Unknown title')}"
            )

            lines.append("")
            lines.append(
                f"- **Status:** "
                f"{verification.get('status', 'Unknown')}"
            )
            lines.append(
                f"- **Message:** "
                f"{verification.get('message', 'Not available')}"
            )
            lines.append("")

    else:

        lines.append("No metadata verification results available.")
        lines.append("")

    # CLAIM VERIFICATION

    lines.append("## Claim Verification")
    lines.append("")

    verification = result.get("claim_verification", {}) or {}

    lines.append(
        f"**Overall Status:** "
        f"{verification.get('verification_status', 'Unknown')}"
    )

    lines.append("")

    if verification.get("reason"):

        lines.append(
            f"**Reason:** {verification.get('reason')}"
        )
        lines.append("")

    claims = verification.get("claims", [])

    if claims:

        for index, claim in enumerate(claims, start=1):

            lines.append(f"### Claim {index}")
            lines.append("")
            lines.append(
                f"- **Statement:** {claim.get('statement', '')}"
            )
            lines.append(
                f"- **Status:** {claim.get('status', 'Unknown')}"
            )
            lines.append(
                f"- **Explanation:** {claim.get('explanation', '')}"
            )
            lines.append(
                f"- **Supporting Sources:** "
                f"{claim.get('supporting_sources', [])}"
            )
            lines.append("")

    else:

        lines.append("No individual claim results available.")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "*This report was generated by the Autonomous AI Research Agent. "
        "Always consult the original research papers before relying on "
        "generated summaries, claims or conclusions.*"
    )

    return "\n".join(lines)


def create_export_filename(topic, extension):
    """
    Create a safe filename using the research topic.
    """

    filename = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        topic.strip()
    ).strip("_")

    if not filename:
        filename = "research_report"

    filename = filename[:60]

    return f"{filename}.{extension}"
