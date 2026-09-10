from services.gemini_service import model


class QuestionResolutionService:

    def is_question_resolved(
        self,
        question: str,
        context: str
    ):

        prompt = f"""
You are evaluating whether a newly uploaded document resolves a previously unanswered question.

Question:
{question}

Retrieved Context:
{context}

Rules:
- Reply ONLY with YES or NO.
- Reply YES only if the context clearly and completely answers the question.
- Reply NO if the context is unrelated, incomplete, or only partially answers the question.
- Do not explain your reasoning.
"""

        response = model.generate_content(prompt)

        answer = response.text.strip().upper()

        return answer == "YES"