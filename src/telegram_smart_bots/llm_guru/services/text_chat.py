import logging

import yaml

from telegram_smart_bots.shared.chat import beam_chat
from telegram_smart_bots.shared.mongo import mongodb_manager

logger = logging.getLogger(__name__)


async def text_chat_service(user_id, message_text):
    db = mongodb_manager.get_database("travel-gurus")
    collection = db["guru"]
    try:
        result = await collection.find_one({"telegram_id": user_id})
        if result is None:
            messages = []
            with open("scripts/config.yml", "r") as stream:
                config = yaml.load(stream, Loader=yaml.Loader)
            new_messages = [config.get("system"), message_text]
        else:
            messages = result.get("messages", [])
            new_messages = [message_text]
        response = await beam_chat({"messages": messages + new_messages})
        new_messages += [response]
        await collection.update_one(
            {"telegram_id": user_id},
            {"$push": {"messages": {"$each": new_messages}}},
            upsert=True,
        )
        msg_reply = response
    except Exception as ex:
        logger.error(ex)
        msg_reply = "😿"
    return msg_reply
