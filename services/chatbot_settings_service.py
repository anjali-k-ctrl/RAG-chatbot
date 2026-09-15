from datetime import datetime, UTC

from database.mongo_helpers import get_chatbot_settings_collection


def get_chatbot_status() -> bool:
    collection = get_chatbot_settings_collection()

    setting = collection.find_one({"_id": "chatbot_settings"})

    # First run: create the setting with chatbot enabled
    if setting is None:
        setting = {
            "_id": "chatbot_settings",
            "enabled": True,
            "updated_at": datetime.now(UTC)
        }

        collection.insert_one(setting)

        return True

    return setting["enabled"]


def set_chatbot_status(enabled: bool) -> bool:
    collection = get_chatbot_settings_collection()

    result = collection.update_one(
        {"_id": "chatbot_settings"},
        {
            "$set": {
                "enabled": enabled,
                "updated_at": datetime.now(UTC)
            }
        },
        upsert=True
    )

    return enabled