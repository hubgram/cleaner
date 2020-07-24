import time
import logging
from pyrogram import Filters, Message
from pyrogram.errors import RPCError, FloodWait
from ..cleaner import Cleaner
from ..utils import supergroup, admin

log = logging.getLogger(__name__)


@Cleaner.on_message(admin & supergroup & Filters.command('clear', prefixes=['!/#']))
def clear(bot: Cleaner, message: Message):

    assert bot.lock(message.chat.id)  # maybe alert by a message

    # TODO: check permission (delete user history)

    def get_recent_user_ids():
        while True:
            last_messages = bot.get_history(message.chat.id)
            yield set(msg.from_user.id for msg in last_messages)

            if len(last_messages) < 100:  # are we done?!
                return

    for user_ids in get_recent_user_ids():
        for user_id in user_ids:
            while True:
                try:
                    bot.delete_user_messages(message.chat.id, user_id)
                except FloodWait as e:
                    time.sleep(e.x + 0.5)
                    continue
                except RPCError as e:
                    log.warning(e)
                break

    bot.unlock(message.chat.id)
    bot.send_message(message.chat.id, '✢✢✢✢')
