__version__ = '0.0.1'

from pyrogram import Filters

supergroup = Filters.create(lambda _, m: bool(m.chat and m.chat.type == "supergroup"), "SuperGroupFilter")
admin = Filters.create(lambda _, m: bool(m.from_user and m._client.is_admin(m.from_user.id)), "AdminFilter")