from configparser import ConfigParser
import pyrogram
from pyrogram.api.functions.channels import DeleteUserHistory
from .utils.fake_client import FakeClient

pyrogram.client.client.Session.notice_displayed = True


class Cleaner(FakeClient, pyrogram.Client):

    def __init__(self):

        # list of groups in cleaning progress
        self._locked_groups = []
        self._admin_ids = set()
        name = self.__class__.__name__.lower()
        super().__init__(
            name,
            config_file=name + '.ini',
            workers=15,
            plugins=dict(root=name + '/plugins'),
            workdir='.'
        )
        self.parse_mode = 'html'

    @property
    def locked_groups(self):
        return self.locked_groups.copy()

    def is_admin(self, user_id: int):
        return user_id in self._admin_ids

    def start(self):
        super().start()
        print('Cleaner bot Started!')

    def stop(self, block: bool = True):
        super().stop(block=block)
        print('Cleaner bot Stopped!')

    def delete_user_messages(self, chat_id, user_id):
        """
        delete all messages from a user in chat
        Parameters:
            chat_id
                chat identifier
            user_id
                user identifier
        """
        return self.send(
            DeleteUserHistory(
                channel=self.resolve_peer(chat_id),
                user_id=self.resolve_peer(user_id)
            )
        )

    def unlock(self, chat_id: int) -> bool:
        if chat_id not in self._locked_groups:
            return False
        else:
            self._locked_groups.remove(chat_id)
            return True

    def lock(self, chat_id: int) -> bool:
        if chat_id in self._locked_groups:
            return False
        else:
            self._locked_groups.append(chat_id)
            return True

    def load_config(self):
        parser = ConfigParser()
        parser.read(str(self.config_file))

        if self.api_id and self.api_hash:
            pass
        else:
            if parser.has_section("cleaner"):
                self.api_id = parser.getint("cleaner", "api_id")
                self.api_hash = parser.get("cleaner", "api_hash")
            else:
                raise AttributeError("No API Key found. More info: https://core.telegram.org/api/obtaining_api_id")

        self._admin_ids.add(parser.getint('cleaner', 'admin_id'))

        for option in ["app_version", "device_model", "system_version", "lang_code"]:
            if getattr(self, option):
                pass
            else:
                if parser.has_section("cleaner"):
                    setattr(self, option, parser.get(
                        "cleaner",
                        option,
                        fallback=getattr(Cleaner, option.upper())
                    ))
                else:
                    setattr(self, option, getattr(Cleaner, option.upper()))
        super().load_config()
