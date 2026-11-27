import streamlit as st
from pathlib import Path

from src.application.research_service import run_research
from src.agents.followup_agent import answer_followup_question
from src.storage.research_history import (
    load_research_history,
    get_research_by_id
)
from src.exporting.export_generator import (
    export_research_json,
    export_research_markdown,
    create_export_filename
)
from src.comparison.research_comparator import compare_research_topics
from src.llm.ollama_client import check_gemini_connection


# ------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🧠",
    layout="wide"
)

# ------------------------------------------
# GEMINI API STATUS
# ------------------------------------------

gemini_status = check_gemini_connection()

if gemini_status["available"]:
    st.success("Gemini API key is configured.")
else:
    st.error(
        "Gemini API key is not configured. "
        "Please add GEMINI_API_KEY to your Streamlit secrets."
    )
# ------------------------------------------
# SESSION STATE
# ------------------------------------------

if "research_result" not in st.session_state:
    st.session_state.research_result = None

if "research_error" not in st.session_state:
    st.session_state.research_error = None


# ------------------------------------------
# HEADER
# ------------------------------------------

st.title("🧠 Autonomous AI Research Agent")

st.markdown(
    """
    Discover, analyze and summarize scientific research
    using Gemini API and retrieval-augmented generation.
    """
)

st.divider()


# ------------------------------------------
# SIDEBAR
# ------------------------------------------

with st.sidebar:

    st.header("About the Agent")

    st.write("This application uses:")

    st.markdown(
        """
        - Python
        - LangGraph
        - Gemini API
        - Sentence Transformers
        - FAISS
        - Crossref
        - ReportLab
        """
    )

    st.divider()

    st.caption("Autonomous AI Research Agent | Phase 14")


# ------------------------------------------
# RESEARCH INPUT
# ------------------------------------------

st.header("Start a Research Project")

topic = st.text_area(
    "Enter your research topic",
    placeholder=(
        "Example: Deep learning techniques "
        "for Alzheimer's disease detection"
    ),
    height=100
)

verify_claims = st.checkbox(
    "Enable additional AI claim verification (slower)",
    value=False,
    help="This makes an additional Gemini API request to check generated claims."
)

start_button = st.button(
    "🚀 Start Research",
    type="primary",
    use_container_width=True
)


# ------------------------------------------
# RUN RESEARCH
# ------------------------------------------

if start_button:

    if not topic.strip():
        st.warning("Please enter a research topic.")

    else:
        st.session_state.research_result = None
        st.session_state.research_error = None

        try:
            with st.status(
                "Preparing your research...",
                expanded=True
            ) as status:

                progress_area = st.empty()

                def update_progress(message):
                    progress_area.write(f"⏳ {message}")

                update_progress("Starting research workflow...")

                research_output = run_research(
                    topic,
                    verify_claims=verify_claims,
                    progress_callback=update_progress
                )

                if not isinstance(research_output, dict):
                    raise ValueError(
                        "The research workflow did not return a valid result. "
                        "Check the research service and workflow logs."
                    )

                st.session_state.research_result = research_output

                status.update(
                    label="Research completed successfully!",
                    state="complete",
                    expanded=False
                )

            st.success("Your research report is ready!")

        except Exception as error:
            st.session_state.research_error = str(error)
            st.error("Research failed. Check the error details below.")


# ------------------------------------------
# RESEARCH HISTORY
# ------------------------------------------

st.divider()

st.header("📚 Research History")

history = load_research_history()

if not history:

    st.info(
        "No previous research found. "
        "Complete a research run to see it here."
    )

else:

    st.write(
        f"Total previous research runs: {len(history)}"
    )

    # Create unique dropdown labels.
    # Including the ID prevents duplicate topics from overwriting each other.

    history_options = {
        (
            f"{item.get('topic', 'Untitled')} "
            f"| {item.get('created_at', '')[:19]} "
            f"| {item.get('id', '')}"
        ): item.get("id")
        for item in history
        if item.get("id")
    }

    if history_options:

        selected_history = st.selectbox(
            "Select a previous research topic",
            options=list(history_options.keys()),
            key="research_history_selector"
        )

        selected_id = history_options[selected_history]

        previous_result = get_research_by_id(selected_id)

        if previous_result:

            st.subheader(
                previous_result.get(
                    "topic",
                    "Previous Research"
                )
            )

            st.caption(
                f"Created at: "
                f"{previous_result.get('created_at', 'Unknown')}"
            )

            # ------------------------------------------
            # PREVIOUS RESEARCH SUMMARY
            # ------------------------------------------

            st.markdown("### Research Summary")

            st.write(
                previous_result.get(
                    "summary",
                    "No summary available."
                )
            )

            # ------------------------------------------
            # PREVIOUS LITERATURE REVIEW
            # ------------------------------------------

            st.markdown("### Literature Review")

            st.write(
                previous_result.get(
                    "literature_review",
                    "No literature review available."
                )
            )

            # ------------------------------------------
            # PREVIOUS RESEARCH ANALYSIS
            # ------------------------------------------

            st.markdown("### Research Analysis")

            st.write(
                previous_result.get(
                    "analysis",
                    "No research analysis available."
                )
            )

            # ------------------------------------------
            # PREVIOUS RESEARCH GAPS
            # ------------------------------------------

            st.markdown("### Research Gaps")

            st.write(
                previous_result.get(
                    "research_gaps",
                    "No research gaps available."
                )
            )

            # ------------------------------------------
            # PREVIOUS RESEARCH SOURCES
            # ------------------------------------------

            st.markdown("### Research Sources")

            sources = previous_result.get("sources", [])

            if sources:

                for index, source in enumerate(
                    sources,
                    start=1
                ):

                    with st.expander(
                        f"Source {index}: "
                        f"{source.get('title', 'Unknown title')}"
                    ):

                        st.write(
                            "Authors:",
                            source.get("authors", "Unknown")
                        )

                        st.write(
                            "Year:",
                            source.get("year")
                            or source.get("published")
                            or "Unknown"
                        )

                        st.write(
                            "Database:",
                            source.get("source", "Unknown")
                        )

                        st.write(
                            "DOI:",
                            source.get("doi", "Not available")
                        )

                        paper_url = source.get("paper_url", "")

                        if paper_url.startswith(("https://", "http://")):

                            st.markdown(
                                 f"[Open Research Paper]({paper_url})"
                            )

            else:

                st.info("No sources were saved.")

            # ------------------------------------------
            # PREVIOUS CLAIM VERIFICATION
            # ------------------------------------------

            st.markdown("### Claim Verification")

            verification = previous_result.get("claim_verification") or {}

            st.write(
                "Status:",
                verification.get("verification_status", "Unknown")
            )

            st.write(
                verification.get(
                    "reason",
                    "No verification details available."
                )
            )

            claims = verification.get("claims", [])

            if claims:
                for index, claim in enumerate(claims, start=1):
                    with st.expander(f"Claim {index}"):
                        st.write("**Statement:**", claim.get("statement", ""))
                        st.write("**Status:**", claim.get("status", "Unknown"))
                        st.write(
                            "**Supporting sources:**",
                            claim.get("supporting_sources", [])
                        )
                        st.write("**Explanation:**", claim.get("explanation", ""))
            else:
                st.info("No individual claim results are available.")

            # ------------------------------------------
            # PREVIOUS PDF REPORT DOWNLOAD
            # ------------------------------------------

            st.markdown("### Previous PDF Report")

            pdf_path = previous_result.get("pdf_path", "")

            if pdf_path:
                pdf_file = Path(pdf_path)

                if pdf_file.is_file():
                    pdf_bytes = pdf_file.read_bytes()
                    st.download_button(
                        label="📄 Download Previous PDF Report",
                        data=pdf_bytes,
                        file_name=pdf_file.name,
                        mime="application/pdf",
                        key=f"history_pdf_{selected_id}"
                    )
                else:
                    st.warning(
                        "The PDF file could not be found. "
                        "The saved research information is still available."
                    )
            else:
                st.info("No PDF report path was saved for this research run.")

            # ------------------------------------------
            # PREVIOUS RESEARCH JSON AND MARKDOWN EXPORT
            # ------------------------------------------

            st.markdown("### Export Previous Research")

            json_data = export_research_json(previous_result)
            markdown_data = export_research_markdown(previous_result)

            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    label="📥 Download JSON",
                    data=json_data,
                    file_name=create_export_filename(
                        previous_result.get("topic", "research"),
                        "json"
                    ),
                    mime="application/json",
                    key=f"history_json_{selected_id}",
                    use_container_width=True
                )

            with col2:
                st.download_button(
                    label="📥 Download Markdown",
                    data=markdown_data,
                    file_name=create_export_filename(
                        previous_result.get("topic", "research"),
                        "md"
                    ),
                    mime="text/markdown",
                    key=f"history_markdown_{selected_id}",
                    use_container_width=True
                )

# ------------------------------------------
# DISPLAY ERRORS
# ------------------------------------------

if st.session_state.research_error:

    with st.expander("View error details", expanded=True):

        st.code(st.session_state.research_error)


# ------------------------------------------
# DISPLAY CURRENT RESEARCH RESULTS
# ------------------------------------------

result = st.session_state.research_result

if result:

    st.divider()

    st.header("Research Dashboard")

    # ------------------------------------------
    # TOP METRICS
    # ------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Retrieved Passages",
            len(result.get("chunks", []))
        )

    with col2:

        st.metric(
            "Unique Research Papers",
            len(result.get("sources", []))
        )

    with col3:

        claim_status = (
            result.get("claim_verification") or {}
        ).get("verification_status", "Unavailable")

        st.metric(
            "Claim Verification",
            claim_status.replace("_", " ").title()
        )

    st.divider()

    # ------------------------------------------
    # RESULTS TABS
    # ------------------------------------------

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "Summary",
            "Literature Review",
            "Research Analysis",
            "Research Gaps",
            "Sources & Verification",
            "PDF Report"
        ]
    )

    # ------------------------------------------
    # TAB 1: SUMMARY
    # ------------------------------------------

    with tab1:

        st.subheader("Research Summary")

        st.write(
            result.get("summary")
            or "No summary available."
        )

    # ------------------------------------------
    # TAB 2: LITERATURE REVIEW
    # ------------------------------------------

    with tab2:

        st.subheader("Literature Review")

        st.write(
            result.get("literature_review")
            or "No literature review available."
        )

    # ------------------------------------------
    # TAB 3: RESEARCH ANALYSIS
    # ------------------------------------------

    with tab3:

        st.subheader("Research Analysis")

        st.write(
            result.get("analysis")
            or "No research analysis available."
        )

    # ------------------------------------------
    # TAB 4: RESEARCH GAPS
    # ------------------------------------------

    with tab4:

        st.subheader("Identified Research Gaps")

        st.write(
            result.get("research_gaps")
            or "No research gaps available."
        )

    # ------------------------------------------
    # TAB 5: SOURCES AND VERIFICATION
    # ------------------------------------------

    with tab5:

        st.subheader("Research Papers")

        for index, source in enumerate(
            result.get("sources", []),
            start=1
        ):

            with st.expander(
                f"Source {index}: "
                f"{source.get('title', 'Unknown title')}"
            ):

                st.write(
                    "**Authors:**",
                    source.get("authors", [])
                )

                st.write(
                    "**Publication year:**",
                    source.get("published")
                    or source.get("year")
                    or "Unknown"
                )

                st.write(
                    "**Database:**",
                    source.get("source", "Unknown")
                )

                st.write(
                    "**DOI:**",
                    source.get("doi") or "Not available"
                )

                paper_url = source.get("paper_url", "")

                if paper_url.startswith(("https://", "http://")):

                    st.markdown(
                        f"[Open Research Paper]({paper_url})"
                    )

        st.divider()

        st.subheader("DOI Metadata Verification")

        for index, item in enumerate(
            result.get("metadata_results", []),
            start=1
        ):

            source = item["source"]
            verification = item["result"]

            with st.expander(
                f"Paper {index}: "
                f"{source.get('title', 'Unknown title')}"
            ):

                st.write(
                    "**Status:**",
                    verification.get("status", "Unknown")
                )

                st.write(
                    "**Message:**",
                    verification.get("message", "")
                )

                metadata = verification.get("metadata")

                if metadata:

                    st.write(
                        "**Crossref DOI:**",
                        metadata.get("doi", "Not available")
                    )

                    st.write(
                        "**Crossref title:**",
                        metadata.get("title", "Not available")
                    )

                    st.write(
                        "**Authors:**",
                        metadata.get("authors", [])
                    )

                    st.write(
                        "**Year:**",
                        metadata.get("year", "Unknown")
                    )

        st.divider()

        st.subheader("Claim Verification")

        verification = result.get("claim_verification") or {}

        st.write(
            "**Overall status:**",
            verification.get(
                "verification_status",
                "Unavailable"
            )
        )

        if verification.get("reason"):

            st.info(verification["reason"])

        claims = verification.get("claims", [])

        if claims:

            for index, claim in enumerate(claims, start=1):

                with st.expander(f"Claim {index}"):

                    st.write(
                        "**Statement:**",
                        claim.get("statement", "")
                    )

                    st.write(
                        "**Status:**",
                        claim.get("status", "Unknown")
                    )

                    st.write(
                        "**Supporting sources:**",
                        claim.get("supporting_sources", [])
                    )

                    st.write(
                        "**Explanation:**",
                        claim.get("explanation", "")
                    )

        elif verification.get("verification_status") == "not_run":

            st.info(
                "Claim verification was skipped. "
                "No claims have been independently checked."
            )

        else:

            st.info("No individual claim results are available.")

        if verification.get("overall_assessment"):

            st.write("**Overall assessment:**")

            st.write(verification["overall_assessment"])

    # ------------------------------------------
    # TAB 6: PDF REPORT
    # ------------------------------------------

    with tab6:

        st.subheader("Download Research Report")

        pdf_path = result.get("pdf_path", "")

        if pdf_path:

            pdf_file = Path(pdf_path)

            if pdf_file.is_file():

                pdf_bytes = pdf_file.read_bytes()

                st.success("Your research report is ready!")

                st.download_button(
                    label="📄 Download Research Report (PDF)",
                    data=pdf_bytes,
                    file_name=pdf_file.name,
                    mime="application/pdf",
                    use_container_width=True
                )

            else:

                st.error(
                    "The generated PDF file could not be found."
                )

        else:

            st.error("No PDF report path is available.")
    
# ------------------------------------------
# EXPORT CURRENT RESEARCH
# ------------------------------------------

if isinstance(result, dict) and result:

    st.divider()
    st.header("Export Research Data")

    json_data = export_research_json(result)
    markdown_data = export_research_markdown(result)

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="📥 Download Research as JSON",
            data=json_data,
            file_name=create_export_filename(
                result.get("topic", "research"),
                "json"
            ),
            mime="application/json",
            use_container_width=True
        )

    with col2:
        st.download_button(
            label="📥 Download Research as Markdown",
            data=markdown_data,
            file_name=create_export_filename(
                result.get("topic", "research"),
                "md"
            ),
            mime="text/markdown",
            use_container_width=True
        )

# ==========================================
# PHASE 14.5 - FOLLOW-UP RESEARCH QUESTIONS
# ==========================================

if isinstance(result, dict) and result:

    st.divider()

    st.header("💬 Ask Follow-up Research Questions")

    st.write(
        "Ask additional questions about your completed research "
        "without running the entire research workflow again."
    )

    # Store separate conversations for different research topics.

    if "followup_conversations" not in st.session_state:
        st.session_state.followup_conversations = {}

    # Use the current research topic as the conversation identifier.
    followup_topic = result.get("topic", "current_research")

    if followup_topic not in st.session_state.followup_conversations:
        st.session_state.followup_conversations[followup_topic] = []

    conversation = st.session_state.followup_conversations[followup_topic]

    # Display previous questions and answers.

    for message in conversation:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Question input.

    followup_question = st.text_input(
        "Ask a follow-up question",
        placeholder="e.g. What are the main research limitations?",
        key=f"followup_input_{followup_topic}"
    )

    col1, col2 = st.columns([3, 1])

    with col1:

        ask_followup = st.button(
            "Send Question",
            use_container_width=True,
            key=f"ask_followup_{followup_topic}"
        )

    with col2:

        clear_followup = st.button(
            "Clear Chat",
            use_container_width=True,
            key=f"clear_followup_{followup_topic}"
        )

    if clear_followup:

        st.session_state.followup_conversations[followup_topic] = []

        st.rerun()


    if ask_followup:

        if not followup_question.strip():

            st.warning("Please enter a question.")

        else:

            try:

                with st.spinner(
                    "Searching research passages and generating an answer..."
                ):

                    followup_result = answer_followup_question(
                        question=followup_question,
                        research_result=result,
                        conversation_history=conversation,
                        top_k=5
                    )

                # Save the user question and assistant answer.

                conversation.append({
                    "role": "user",
                    "content": followup_question
                })

                conversation.append({
                    "role": "assistant",
                    "content": followup_result["answer"]
                })

                st.session_state.followup_conversations[followup_topic] = conversation

                st.rerun()

            except Exception as error:

                st.error(
                    f"Could not answer the follow-up question: {error}"
                )
        

# ==========================================
# PHASE 14.4 - RESEARCH COMPARISON
# ==========================================

st.divider()

st.header("🔬 Research Comparison")

st.write(
    "Compare two research topics using retrieved research papers "
    "and Gemini AI."
)

if "comparison_result" not in st.session_state:
    st.session_state.comparison_result = None

if "comparison_error" not in st.session_state:
    st.session_state.comparison_error = None


col1, col2 = st.columns(2)

with col1:

    topic_a = st.text_input(
        "Research Topic A",
        placeholder="e.g. CNN for image classification",
        key="comparison_topic_a"
    )

with col2:

    topic_b = st.text_input(
        "Research Topic B",
        placeholder="e.g. Vision Transformers",
        key="comparison_topic_b"
    )


top_k = st.slider(
    "Research passages per topic",
    min_value=1,
    max_value=10,
    value=5,
    key="comparison_top_k"
)


if st.button(
    "🔍 Compare Research Topics",
    use_container_width=True
):

    if not topic_a.strip() or not topic_b.strip():

        st.warning("Please enter both research topics.")

    else:

        st.session_state.comparison_result = None
        st.session_state.comparison_error = None

        with st.spinner(
            "Retrieving research papers and generating comparison..."
        ):

            try:

                comparison_result = compare_research_topics(
                    topic_a=topic_a,
                    topic_b=topic_b,
                    top_k=top_k
                )

                st.session_state.comparison_result = comparison_result

            except Exception as error:

                st.session_state.comparison_error = str(error)


if st.session_state.comparison_error:

    st.error(st.session_state.comparison_error)


if st.session_state.comparison_result:

    comparison_result = st.session_state.comparison_result

    st.success("Research comparison completed!")

    st.markdown(
        f"### {comparison_result['topic_a']} vs "
        f"{comparison_result['topic_b']}"
    )

    st.markdown(comparison_result["comparison"])

    st.divider()

    st.subheader("Retrieved Research Sources")

    source_col1, source_col2 = st.columns(2)

    with source_col1:

        st.markdown("#### Topic A Sources")

        for index, source in enumerate(
            comparison_result["sources_a"],
            start=1
        ):

            with st.expander(
                f"Source {index}: {source.get('title', 'Unknown title')}"
            ):

                st.write(source.get("text", "No passage text available."))

                st.caption(
                    f"Page: {source.get('page_number', 'Unknown')}"
                )

    with source_col2:

        st.markdown("#### Topic B Sources")

        for index, source in enumerate(
            comparison_result["sources_b"],
            start=1
        ):

            with st.expander(
                f"Source {index}: {source.get('title', 'Unknown title')}"
            ):

                st.write(source.get("text", "No passage text available."))

                st.caption(
                    f"Page: {source.get('page_number', 'Unknown')}"
                )
    
    # ------------------------------------------
    # START NEW RESEARCH
    # ------------------------------------------

    st.divider()

    if st.button("Start a New Research Project"):

        st.session_state.research_result = None
        st.session_state.research_error = None

        st.rerun()


# ------------------------------------------
# FOOTER
# ------------------------------------------

st.divider()

st.caption(
    "Autonomous AI Research Agent | "
    "Built using Python, LangGraph, Gemini API and Streamlit"
)
