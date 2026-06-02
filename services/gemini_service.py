import google.generativeai as genai

from config.settings import settings


genai.configure(
    api_key=settings.GEMINI_API_KEY
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


def generate_answer(
    question: str,
    context: str
):

    prompt = f"""
You are a MediaShipper Training Assistant.

STRICT RULES:

- Answer ONLY using the documentation provided.
- Never use external knowledge.
- Never guess.
- Never make assumptions.
- If the answer is not explicitly stated in the documentation, respond exactly:

I could not find this information in the MediaShipper documentation.

- Keep answers concise and factual.
- Do not add information that is not present in the documentation.

DOCUMENTATION:
{context}

QUESTION:
{question}
"""

    print("\n===== CONTEXT SENT TO GEMINI =====\n")
    print(context[:2000])
    print("\n===== QUESTION =====\n")
    print(question)

    response = model.generate_content(prompt)

    print("\n===== GEMINI RESPONSE =====\n")
    print(response.text)

    return response.text