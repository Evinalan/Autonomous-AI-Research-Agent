
import json
import re

from src.llm.ollama_client import generate_response


def verify_generated_text(generated_text, context):

    """
    Ask the local LLM to compare generated claims
    against the retrieved research passages.
    """

    print("\n[VERIFICATION AGENT] Checking generated claims...")

    prompt = f"""
You are a research evidence verification assistant.

Your job is to check whether the statements in the
AI-generated research answer are supported by the
provided research passages.

RESEARCH PASSAGES:

{context}

AI-GENERATED ANSWER:

{generated_text}

INSTRUCTIONS:

1. Break the answer into important factual claims.
2. Check each claim against the research passages.
3. Identify the supporting source numbers.
4. Do not treat general knowledge as evidence.
5. If no supporting passage exists, mark the claim
   as unsupported.
6. If evidence is incomplete, mark it as partially_supported.
7. Do not invent source numbers or quotations.

Return ONLY valid JSON in this exact structure:

{{
    "claims": [
        {{
            "claim": "A factual statement from the answer",
            "status": "supported",
            "supporting_sources": ["SOURCE 1"],
            "explanation": "Why the evidence supports the claim"
        }}
    ],
    "overall_assessment": "Brief assessment"
}}

Allowed status values:

supported
partially_supported
unsupported

Do not include Markdown code fences.
"""

    try:

        response = generate_response(prompt)

        # Remove possible Markdown code fences.
        response = response.strip()

        response = re.sub(
            r"^```(?:json)?\s*",
            "",
            response,
            flags=re.IGNORECASE
        )

        response = re.sub(
            r"\s*```$",
            "",
            response
        )

        result = json.loads(response)

        if not isinstance(result, dict):
            raise ValueError("Expected a JSON object.")

        if not isinstance(result.get("claims"), list):
            raise ValueError("Missing claims list.")

        allowed_statuses = {
            "supported",
            "partially_supported",
            "unsupported"
        }

        for claim in result["claims"]:

            if claim.get("status") not in allowed_statuses:
                raise ValueError("Invalid claim status.")

            if not isinstance(
                claim.get("supporting_sources", []),
                list
            ):
                raise ValueError("Invalid supporting sources.")

        result["verification_status"] = "completed"

        return result

    except Exception as error:

        return {
            "verification_status": "manual_review_required",
            "error": str(error),
            "claims": [],
            "overall_assessment": (
                "Automatic claim verification could not "
                "be completed. Review the answer manually."
            )
        }


def display_claim_verification(result):

    print("\n" + "=" * 65)
    print("              CLAIM VERIFICATION REPORT")
    print("=" * 65)

    if result.get("verification_status") != "completed":

        print("Status: Manual review required")
        print("Reason:", result.get("error", "Unknown error"))
        return

    for index, claim in enumerate(
        result.get("claims", []),
        start=1
    ):

        print(f"\nCLAIM {index}")
        print("Statement:", claim.get("claim", ""))
        print("Status:", claim.get("status", "unknown"))

        print(
            "Supporting sources:",
            claim.get("supporting_sources", [])
        )

        print(
            "Explanation:",
            claim.get("explanation", "")
        )

    print("\nOverall assessment:")
    print(result.get("overall_assessment", "Not available"))
