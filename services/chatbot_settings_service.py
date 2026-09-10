from database.models import ChatbotSettings
from database.postgres import SessionLocal


def get_chatbot_status() -> bool:
    db = SessionLocal()

    try:
        setting = (
            db.query(ChatbotSettings)
            .filter(ChatbotSettings.id == 1)
            .first()
        )

        # First run: create the setting with chatbot enabled
        if setting is None:
            setting = ChatbotSettings(
                id=1,
                enabled=True
            )

            db.add(setting)
            db.commit()
            db.refresh(setting)

        return setting.enabled

    finally:
        db.close()


def set_chatbot_status(enabled: bool) -> bool:
    db = SessionLocal()

    try:
        setting = (
            db.query(ChatbotSettings)
            .filter(ChatbotSettings.id == 1)
            .first()
        )

        if setting is None:
            setting = ChatbotSettings(
                id=1,
                enabled=enabled
            )

            db.add(setting)

        else:
            setting.enabled = enabled

        db.commit()
        db.refresh(setting)

        return setting.enabled

    finally:
        db.close()