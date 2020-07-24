from typing import Union, List

import pyrogram
from pyrogram.client.ext import BaseClient, utils
from pyrogram.api import functions
from pyrogram.client.methods.messages.search_messages import Filters, POSSIBLE_VALUES


# noinspection PyShadowingBuiltins
def get_chunk(
    client: BaseClient,
    chat_id: Union[int, str],
    query: str = "",
    filter: str = "empty",
    min_date: int = 0,
    max_date: int = 0,
    offset_id: int = 0,
    offset: int = 0,
    limit: int = 100,
    from_user: Union[int, str] = None
) -> List["pyrogram.Message"]:
    try:
        filter = Filters.__dict__[filter.upper()]
    except KeyError:
        raise ValueError('Invalid filter "{}". Possible values are: {}'.format(
            filter, ", ".join('"{}"'.format(v) for v in POSSIBLE_VALUES))) from None

    r = client.send(
        functions.messages.Search(
            peer=client.resolve_peer(chat_id),
            q=query,
            filter=filter,
            min_date=min_date,
            max_date=max_date,
            offset_id=offset_id,
            add_offset=offset,
            limit=limit,
            min_id=0,
            max_id=0,
            from_id=(
                client.resolve_peer(from_user)
                if from_user
                else None
            ),
            hash=0
        )
    )

    return utils.parse_messages(client, r, replies=0)  # no replies :)
