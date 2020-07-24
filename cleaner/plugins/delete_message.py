import time
import logging
from itertools import islice
from pyrogram import Filters, Message, Emoji
from pyrogram.errors import RPCError, FloodWait
from ..cleaner import Cleaner
from ..utils import admin

log = logging.getLogger(__name__)

# TODO: change photo_video to media and voice_note to voice. maybe add poll and venue
CONTENT_TYPES = ['text', 'photo_video', 'audio', 'document', 'photo', 'sticker', 'video', 'animation', 'voice_note',
                 'video_note', 'contact', 'location', 'url']


@Cleaner.on_message(admin & Filters.group & Filters.regex(r'^[!/#]?del ({})? ?(\d+)?$'.format('|'.join(CONTENT_TYPES))))
def delete_message(bot: Cleaner, message: Message):
    """
    delete messages
    (mtype) specific kind of message to be deleted. by default (empty) all kind of message will be deleted
    (total) number of messages to be deleted. by default: (0 or empty) all messages will be deleted
    if message is replied to a user message. that user messages will be deleted without considering the type
    """

    assert bot.lock(message.chat.id)  # maybe alert by a message

    # TODO: check permission (delete message and user history)

    notify_message = message.reply('Start cleaning process...')

    mtype, total = message.matches[0].groups()
    total = total and int(total) or 0
    message_type = mtype and ' <b>{}</b>'.format(mtype.upper()) or ''
    from_user_id = None

    if message.reply_to_message and message.reply_to_message.from_user:

        from_user = message.reply_to_message.from_user
        from_user_id = from_user.id
        if not total:
            try:
                bot.delete_user_messages(message.chat.id, from_user_id)
                notify_message.edit('All messages from {:mention}) deleted'.format(from_user))
            except RPCError as e:
                log.warning(e)
            return bot.unlock(message.chat.id)
        if mtype:
            message_type = ' <s>{}</s>'.format(mtype.upper())

        mtype = 'empty'

    def get_message_ids():

        if mtype:
            if mtype in ('text', 'sticker'):
                msgs = islice(
                    filter(lambda m: getattr(m, mtype), bot.iter_history(
                        chat_id=message.chat.id, offset_id=total and message.message_id or 0
                    )),
                    total or None
                )
            else:
                msgs = bot.search_messages(
                    chat_id=message.chat.id, filter=mtype, limit=total,
                    offset_id=message.message_id, from_user=from_user_id
                )
        else:
            msgs = bot.iter_history(
                chat_id=message.chat.id,
                offset_id=message.message_id or 0, limit=total,
                reverse=False
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
                total_deleted_message += len(message_ids)  # if group is migrated then it may be +1
            except FloodWait as e:
                time.sleep(e.x + 0.5)
                continue
            except RPCError as e:
                log.warning(e)
            break

    bot.unlock(message.chat.id)
    notify_message.edit('<b>{}</b>{} messages deleted 🗑'.format(total_deleted_message, message_type))
