
from pathlib import Path
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle
)


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# PDF output directory
REPORT_FOLDER = PROJECT_ROOT / "reports"


def safe_text(value):
    """
    Safely convert text for ReportLab Paragraphs.
    """

    if value is None:
        return "Not available"

    if isinstance(value, (list, tuple)):
        value = ", ".join(str(item) for item in value)

    if isinstance(value, dict):
        value = str(value)

    return escape(str(value)).replace("\n", "<br/>")


def create_styles():

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=22,
            leading=28,
            alignment=TA_CENTER,
            spaceAfter=20
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading1"],
            fontSize=15,
            leading=20,
            textColor=colors.HexColor("#17365D"),
            spaceBefore=16,
            spaceAfter=10
        )
    )

    styles.add(
        ParagraphStyle(
            name="ReportBody",
            parent=styles["BodyText"],
            fontSize=9.5,
            leading=15,
            spaceAfter=9
        )
    )

    styles.add(
        ParagraphStyle(
            name="SmallText",
            parent=styles["BodyText"],
            fontSize=8,
            leading=11
        )
    )

    return styles


def add_paragraphs(story, text, style):
    """
    Add text as paragraphs.
    """

    if not text:
        story.append(
            Paragraph("Not available.", style)
        )
        return

    for block in str(text).split("\n\n"):

        block = block.strip()

        if block:
            story.append(
                Paragraph(safe_text(block), style)
            )


def add_section(story, heading, content, styles):

    story.append(
        Paragraph(
            safe_text(heading),
            styles["SectionHeading"]
        )
    )

    add_paragraphs(
        story,
        content,
        styles["ReportBody"]
    )


def add_references(story, sources, metadata_results, styles):

    story.append(
        Paragraph(
            "References",
            styles["SectionHeading"]
        )
    )

    if not sources:

        story.append(
            Paragraph(
                "No references were available.",
                styles["ReportBody"]
            )
        )
        return

    for index, source in enumerate(sources, start=1):

        verification = metadata_results[index - 1]

        result = verification.get("result", {})
        metadata = result.get("metadata") or {}

        title = (
            metadata.get("title")
            or source.get("title")
            or "Unknown title"
        )

        authors = (
            metadata.get("authors")
            or source.get("authors")
            or []
        )

        year = (
            metadata.get("year")
            or source.get("published")
            or "Unknown year"
        )

        doi = (
            metadata.get("doi")
            or source.get("doi")
            or "Not available"
        )

        url = (
            source.get("paper_url")
            or source.get("pdf_url")
            or ""
        )

        reference_text = (
            f"<b>[{index}]</b> "
            f"{safe_text(authors)}. "
            f"({safe_text(year)}). "
            f"<i>{safe_text(title)}</i>. "
            f"DOI: {safe_text(doi)}."
        )

        if url and url.startswith(("https://", "http://")):

            safe_url = escape(url, {'"': "&quot;"})

            reference_text += (
                f' <link href="{safe_url}" color="blue">'
                "Open paper</link>."
            )

        story.append(
            Paragraph(
                reference_text,
                styles["ReportBody"]
            )
        )

        story.append(Spacer(1, 5))


def add_claim_verification(story, verification, styles):

    story.append(
        Paragraph(
            "Claim Verification",
            styles["SectionHeading"]
        )
    )

    if not verification:

        story.append(
            Paragraph(
                "Claim verification was unavailable.",
                styles["ReportBody"]
            )
        )
        return

    claims = verification.get("claims", [])

    if not claims:

        story.append(
            Paragraph(
                safe_text(
                    verification.get(
                        "overall_assessment",
                        verification.get(
                            "reason",
                            "No claim details available."
                        )
                    )
                ),
                styles["ReportBody"]
            )
        )
        return

    table_data = [
        [
            Paragraph("<b>Claim</b>", styles["SmallText"]),
            Paragraph("<b>Status</b>", styles["SmallText"]),
            Paragraph("<b>Sources</b>", styles["SmallText"])
        ]
    ]

    for claim in claims:

        statement = claim.get("statement", "")
        status = claim.get("status", "Unknown")
        sources = claim.get("supporting_sources", [])

        table_data.append(
            [
                Paragraph(safe_text(statement), styles["SmallText"]),
                Paragraph(safe_text(status), styles["SmallText"]),
                Paragraph(safe_text(sources), styles["SmallText"])
            ]
        )

    table = Table(
        table_data,
        colWidths=[3.5 * inch, 1.1 * inch, 1.5 * inch],
        repeatRows=1
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(table)

    overall = verification.get("overall_assessment", "")

    if overall:

        story.append(Spacer(1, 10))

        story.append(
            Paragraph(
                safe_text(overall),
                styles["ReportBody"]
            )
        )


def add_page_number(canvas, doc):

    canvas.saveState()

    canvas.setFont("Helvetica", 8)

    canvas.drawString(
        0.75 * inch,
        0.45 * inch,
        "Autonomous AI Research Agent"
    )

    canvas.drawRightString(
        7.75 * inch,
        0.45 * inch,
        f"Page {doc.page}"
    )

    canvas.restoreState()


def generate_research_report(report_data):

    REPORT_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"research_report_{timestamp}.pdf"

    output_path = REPORT_FOLDER / filename

    styles = create_styles()

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=report_data.get("topic", "Research Report"),
        author="Autonomous AI Research Agent"
    )

    story = []

    topic = report_data.get(
        "topic",
        "Research Report"
    )

    # TITLE PAGE

    story.append(Spacer(1, 1.5 * inch))

    story.append(
        Paragraph(
            "AUTONOMOUS AI RESEARCH AGENT",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 0.5 * inch))

    story.append(
        Paragraph(
            safe_text(topic),
            styles["ReportTitle"]
        )
    )

    story.append(
        Paragraph(
            "AI-Generated Research Report",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 0.5 * inch))

    story.append(
        Paragraph(
            "Generated on: "
            + datetime.now().strftime("%d %B %Y, %H:%M"),
            styles["ReportBody"]
        )
    )

    story.append(Spacer(1, 2 * inch))

    story.append(
        Paragraph(
            "This report was generated using locally run "
            "AI research agents, retrieved research passages, "
            "and available metadata verification results.",
            styles["ReportBody"]
        )
    )

    story.append(PageBreak())

    # ABSTRACT

    add_section(
        story,
        "Abstract",
        report_data.get("summary", ""),
        styles
    )

    # INTRODUCTION

    add_section(
        story,
        "1. Introduction",
        report_data.get(
            "introduction",
            "This report examines the research topic: " + topic
        ),
        styles
    )

    # LITERATURE REVIEW

    add_section(
        story,
        "2. Literature Review",
        report_data.get("literature_review", ""),
        styles
    )

    # RESEARCH ANALYSIS

    add_section(
        story,
        "3. Research Analysis",
        report_data.get("analysis", ""),
        styles
    )

    # RESEARCH GAPS

    add_section(
        story,
        "4. Research Gaps and Future Directions",
        report_data.get("research_gaps", ""),
        styles
    )

    # CLAIM VERIFICATION

    add_claim_verification(
        story,
        report_data.get("claim_verification"),
        styles
    )

    # DOI VERIFICATION SUMMARY

    add_section(
        story,
        "Metadata Verification Notes",
        report_data.get(
            "verification_notes",
            "Metadata verification results are listed with the references."
        ),
        styles
    )

    # CONCLUSION

    add_section(
        story,
        "5. Conclusion",
        report_data.get(
            "conclusion",
            report_data.get("summary", "")
        ),
        styles
    )

    # REFERENCES

    add_references(
        story,
        report_data.get("sources", []),
        report_data.get("metadata_results", []),
        styles
    )

    # IMPORTANT DISCLAIMER

    add_section(
        story,
        "Research Disclaimer",
        (
            "This report is an AI-assisted research summary, "
            "not a substitute for reading and evaluating the original "
            "research papers. Claim verification is automated and may "
            "contain errors. DOI metadata matches should also be "
            "checked against the original publication. "
            "Medical findings should not be treated as clinical advice."
        ),
        styles
    )

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    return output_path
