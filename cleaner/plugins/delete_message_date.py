import time
import logging
from itertools import takewhile
from pyrogram import Filters, Message
from pyrogram.errors import RPCError, FloodWait
from ..cleaner import Cleaner
from ..utils import admin

log = logging.getLogger(__name__)


@Cleaner.on_message(admin & Filters.group and Filters.regex(r'^[!/#]?del (-)?(?:(\d+)(?:h|hour))?[ :]?(?:(\d+)(?:m|min))?$'))
def delete_message_date(bot: Cleaner, message: Message):
    """
    delete messages before or after x hour and y minute ago
    (-) for messages before date
    """

    until_date, hour, minute = message.matches[0].groups()

    assert bot.lock(message.chat.id)  # maybe alert by a message

    # TODO: check permission (delete message and user history)

    notify_message = message.reply(
        'Deleting Messages {} {}{}{} ago'.format(
            'until' if until_date else 'before',
            hour + 'h' if hour else '', ' and ' if hour and minute else '',
            minute + 'min'
        )
    )

    hour = int(hour) if hour else 0
    minute = int(minute) if minute else 0

    if not (hour or minute):
        return

    def get_message_ids():
        offset_date = int(time.time() - hour*3600 - minute*60)
        if until_date:
            msgs = bot.iter_history(
                chat_id=message.chat.id, offset_date=offset_date)
        else:
            # why with offset_date and reverse=True not working :| buggy pyrogram?!
            msgs = takewhile(
                lambda m: m.date >= offset_date,
                bot.iter_history(chat_id=message.chat.id, offset_id=message.message_id)
            )
        msg_ids = []
        for msg in msgs:
            msg_ids.append(msg.message_id)
            if len(msg_ids) == 100:
                yield msg_ids
                msg_ids = []
        else:
            if msg_ids:
                yield msg_ids

    total_deleted_message = 0
    for message_ids in get_message_ids():
        while True:
            try:
                bot.delete_messages(message.chat.id, message_ids)
                total_deleted_message += len(message_ids)
            except FloodWait as e:
                time.sleep(e.x + 0.5)
                continue
            except RPCError as e:
                log.warning(e)
            break

    bot.unlock(message.chat.id)
    notify_message.edit('<b>{}</b> messages deleted 🗑'.format(total_deleted_message))
