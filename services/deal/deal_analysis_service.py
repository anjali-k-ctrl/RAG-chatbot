
import json
import re

from services.gemini_service import model


def analyze_proposal(extracted_text: str) -> dict:
    """
    Extract structured licensing terms from a proposal
    and identify missing or ambiguous information.
    """

    prompt = f"""
You are a licensing agreement analysis assistant.

Analyze the following licensing proposal.

Extract only information explicitly supported by the document.
Never invent or assume missing values.

Return ONLY valid JSON in this exact structure:

{{
    "extracted_terms": {{
        "title": null,
        "buyer": null,
        "seller": null,
        "rights_type": null,
        "license_start_date": null,
        "license_end_date": null,
        "license_duration": null,
        "exclusivity": null,
        "license_fee": null,
        "revenue_share": null,
        "payment_schedule": null,
        "delivery_requirements": null,
        "restrictions_and_conditions": null
    }},
    "missing_information": [],
    "ambiguous_information": [],
    "summary": ""
}}

Rules:

1. Use null when a term is not mentioned.
2. Identify important missing licensing information.
3. Identify clauses that are unclear, contradictory,
   or require clarification.
4. Do not provide legal advice.
5. Do not invent values.
6. Do not include territory as an extraction field.
7. Keep the summary concise.
8. Return valid JSON only, without Markdown.

LICENSING PROPOSAL:

{extracted_text[:30000]}
"""

    response = model.generate_content(prompt)

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    result_text = response.text.strip()

    # Remove Markdown code fences if returned
    result_text = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        result_text
    )

    try:
        result = json.loads(result_text)
    except json.JSONDecodeError:
        raise ValueError(
            "Gemini returned an invalid JSON response."
        )

    required_keys = [
        "extracted_terms",
        "missing_information",
        "ambiguous_information",
        "summary"
    ]

    if not isinstance(result, dict) or not all(
        key in result for key in required_keys
    ):
        raise ValueError("Gemini returned an unexpected response structure.")

    if not isinstance(result["extracted_terms"], dict):
        raise ValueError("Invalid extracted terms structure.")

    if not isinstance(result["missing_information"], list):
        raise ValueError("Invalid missing information structure.")

    if not isinstance(result["ambiguous_information"], list):
        raise ValueError("Invalid ambiguous information structure.")

    if not isinstance(result["summary"], str):
        raise ValueError("Invalid summary.")

    return result
