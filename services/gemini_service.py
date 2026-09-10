import json
import google.generativeai as genai

from config.settings import settings


genai.configure(
    api_key=settings.GEMINI_API_KEY
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


UNSUPPORTED_MESSAGE = (
    "I'm only able to help with MediaShippers-related questions — "
    "like deals, rights, payments, content submissions, and buyer/seller "
    "rules. Please ask me something about the MediaShippers platform!"
)


def generate_answer(
    question: str,
    chunks: list
):

    primary_source = None

    if chunks:
        primary_source = chunks[0].get("document_name")


    # --------------------------------------------------
    # FORMAT RETRIEVED CONTEXT
    # --------------------------------------------------

    formatted_context = ""

    for i, chunk in enumerate(chunks, start=1):

        formatted_context += f"""
DOCUMENT {i}

Retrieval Rank:
{i}

Retrieval Score:
{chunk.get("score")}

Document ID:
{chunk.get("document_id")}

Document Name:
{chunk.get("document_name")}

Page:
{chunk.get("page_name")}

Uploaded At:
{chunk.get("uploaded_at")}

Content:
{chunk.get("text")}

----------------------------------------
"""


    # --------------------------------------------------
    # MAIN GEMINI PROMPT
    # --------------------------------------------------

    prompt = f"""
    You are the MediaShippers Knowledge Assistant.

    Your job is to answer the user's question using ONLY the provided
    MediaShippers documentation.

    The documentation below was retrieved from the MediaShippers
    knowledge base using semantic vector search.

    IMPORTANT RULES:

    1. Use ONLY information contained in the provided documentation.

    2. Never use external knowledge.

    3. Never guess, assume, or invent information.

    4. If the documentation fully answers the question, provide a clear answer.

    5. If the documentation answers ONLY PART of the question:
    - Answer the part that is supported by the documentation.
    - Clearly state that the remaining part is not covered in the
        provided documentation.
    - DO NOT reject the entire question.

    6. Do NOT say that a question is unrelated to MediaShippers if relevant
    MediaShippers documentation has been provided.

    7. If NONE of the provided documentation contains information relevant
    to the user's question, say that the information could not be found
    in the available MediaShippers documentation.

    8. Never introduce facts that are not supported by the retrieved
    documentation.

    9. When multiple documents contain similar information, use the most
    relevant retrieved information.

    10. Do not combine conflicting information from different documents.

    11. If the retrieved documentation contains conflicting information,
        prefer the higher-ranked relevant retrieval result.

    12. Return ONLY valid JSON.

    13. Do NOT wrap the JSON in markdown.

    14. Do NOT include explanations outside the JSON.

    Return exactly this format:

    {{
        "answer": "...",
        "followups": []
    }}

    If NONE of the documentation contains relevant information, return:

    {{
        "answer": "{UNSUPPORTED_MESSAGE}",
        "followups": []
    }}

    DOCUMENTATION:

    {formatted_context}

    USER QUESTION:

    {question}
    """


    # --------------------------------------------------
    # DEBUG LOGGING
    # --------------------------------------------------

    print("\n===== CONTEXT SENT TO GEMINI =====\n")
    print(formatted_context[:3000])

    print("\n===== QUESTION =====\n")
    print(question)


    # --------------------------------------------------
    # GENERATE ANSWER
    # --------------------------------------------------

    response = model.generate_content(
        prompt
    )

    print("\n===== RAW GEMINI RESPONSE =====\n")
    print(response.text)


    # --------------------------------------------------
    # PARSE GEMINI RESPONSE
    # --------------------------------------------------

    try:

        result = json.loads(
            response.text
        )

    except json.JSONDecodeError:

        print(
            "Gemini returned invalid JSON."
        )

        return {
            "answer": UNSUPPORTED_MESSAGE,
            "followups": [],
            "source_document": primary_source
        }


    answer = result.get(
        "answer",
        UNSUPPORTED_MESSAGE
    )


    # --------------------------------------------------
    # FOLLOW-UP QUESTIONS
    # --------------------------------------------------

    followup_prompt = f"""
Based ONLY on the MediaShippers documentation below,
generate exactly 3 useful follow-up questions related
to the user's question.

Rules:

- Only generate questions.
- Maximum 10 words per question.
- One question per line.
- Do not number the questions.
- Do not answer the questions.
- Do not use external knowledge.
- Questions must be supported by the provided documentation.
- Avoid repeating the user's exact question.

DOCUMENTATION:

{formatted_context}

USER QUESTION:

{question}
"""


    followup_questions = []

    try:

        followup_response = model.generate_content(
            followup_prompt
        )

        followup_questions = [
            q.strip("-• ").strip()
            for q in followup_response.text.split("\n")
            if q.strip()
        ][:3]

    except Exception as e:

        print(
            f"Follow-up generation failed: {e}"
        )

        followup_questions = []

    return {
        "answer": answer,
        "followups": followup_questions,
        "source_document": primary_source
    }