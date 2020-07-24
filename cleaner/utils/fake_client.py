# just a fake client of pyrogram.client with tiny little small changes

import logging
import time
from typing import Union, List, Generator
import pyrogram
from pyrogram.api import functions
from pyrogram.client.ext import BaseClient, utils
from pyrogram.errors import RPCError, FloodWait
from .get_chunk import get_chunk

log = logging.getLogger(__name__)


class FakeClient(BaseClient):

    UPDATES_WORKERS = 10

    def get_history(
        self,
        chat_id: Union[int, str],
        limit: int = 100,
        offset: int = 0,
        offset_id: int = 0,
        offset_date: int = 0,
        reverse: bool = False
    ) -> List["pyrogram.Message"]:
        """Retrieve a chunk of the history of a chat.

        You can get up to 100 messages at once.
        For a more convenient way of getting a chat history see :meth:`~Client.iter_history`.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            limit (``int``, *optional*):
                Limits the number of messages to be retrieved.
                By default, the first 100 messages are returned.

            offset (``int``, *optional*):
                Sequential number of the first message to be returned. Defaults to 0 (most recent message).
                Negative values are also accepted and become useful in case you set offset_id or offset_date.

            offset_id (``int``, *optional*):
                Pass a message identifier as offset to retrieve only older messages starting from that message.

            offset_date (``int``, *optional*):
                Pass a date in Unix time as offset to retrieve only older messages starting from that date.

            reverse (``bool``, *optional*):
                Pass True to retrieve the messages in reversed order (from older to most recent).

        Returns:
            List of :obj:`Message` - On success, a list of the retrieved messages is returned.

        Example:
            .. code-block:: python

                # Get the last 100 messages of a chat
                app.get_history("pyrogramchat")

                # Get the last 3 messages of a chat
                app.get_history("pyrogramchat", limit=3)

                # Get 3 messages after skipping the first 5
                app.get_history("pyrogramchat", offset=5, limit=3)
        """

        offset_id = offset_id or (1 if reverse else 0)

        while True:
            try:
                messages = utils.parse_messages(
                    self,
                    self.send(
                        functions.messages.GetHistory(
                            peer=self.resolve_peer(chat_id),
                            offset_id=offset_id,
                            offset_date=offset_date,
                            add_offset=offset * (-1 if reverse else 1) - (limit if reverse else 0),
                            limit=limit,
                            max_id=0,
                            min_id=0,
                            hash=0
                        )
                    ),
                    replies=0
                )  # no replies :)
            except FloodWait as e:
                log.warning("Sleeping for {}s".format(e.x))
                time.sleep(e.x)
                continue
            except RPCError as e:
                log.warning(e)
                messages = []

            if reverse:
                messages.reverse()

            return messages

    # TODO: add other parameters
    # noinspection PyShadowingBuiltins
    def search_messages(
            self,
            chat_id: Union[int, str],
            query: str = "",
            min_date: int = 0,
            max_date: int = 0,
            offset_id: int = 0,
            offset: int = 0,
            filter: str = "empty",
            limit: int = 0,
            from_user: Union[int, str] = None
    ) -> Generator["pyrogram.Message", None, None]:
        """Search for text and media messages inside a specific chat.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            query (``str``, *optional*):
                Text query string.
                Required for text-only messages, optional for media messages (see the ``filter`` argument).
                When passed while searching for media messages, the query will be applied to captions.
                Defaults to "" (empty string).

            offset (``int``, *optional*):
                Sequential number of the first message to be returned.
                Defaults to 0.

            filter (``str``, *optional*):
                Pass a filter in order to search for specific kind of messages only:

                - ``"empty"``: Search for all kind of messages (default).
                - ``"photo"``: Search for photos.
                - ``"video"``: Search for video.
                - ``"photo_video"``: Search for either photo or video.
                - ``"document"``: Search for documents (generic files).
                - ``"url"``: Search for messages containing URLs (web links).
                - ``"animation"``: Search for animations (GIFs).
                - ``"voice_note"``: Search for voice notes.
                - ``"audio"``: Search for audio files (music).
                - ``"chat_photo"``: Search for chat photos.
                - ``"phone_call"``: Search for phone calls.
                - ``"audio_video_note"``: Search for either audio or video notes.
                - ``"video_note"``: Search for video notes.
                - ``"mention"``: Search for messages containing mentions to yourself.
                - ``"location"``: Search for location messages.
                - ``"contact"``: Search for contact messages.

            limit (``int``, *optional*):
                Limits the number of messages to be retrieved.
                By default, no limit is applied and all messages are returned.

            from_user (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user you want to search for messages from.

        Returns:
            ``Generator``: A generator yielding :obj:`Message` objects.

        Example:
            .. code-block:: python

                # Search for text messages in @pyrogramchat. Get the last 333 results
                for message in app.search_messages("pyrogramchat", query="dan", limit=333):
                    print(message.text)

                # Search for photos sent by @haskell in @pyrogramchat
                for message in app.search_messages("pyrogramchat", "", filter="photo" limit=333, from_user="haskell"):
                    print(message.text)
        """
        current = 0
        total = abs(limit) or (1 << 31) - 1
        limit = min(100, total)

        while True:
            try:
                messages = get_chunk(
                    client=self,
                    chat_id=chat_id,
                    query=query,
                    filter=filter,
                    min_date=min_date,
                    max_date=max_date,
                    offset_id=offset_id,
                    offset=offset,
                    limit=limit,
                    from_user=from_user
                )
            except FloodWait as e:
                log.warning("Sleeping for {}s".format(e.x))
                time.sleep(e.x)
                continue
            except RPCError as e:
                log.warning(e)
                messages = []

            if not messages:
                return

            offset += 100

            for message in messages:
                yield message

                current += 1

                if current >= total:
                    return
