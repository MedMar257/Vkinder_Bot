from commands import commands
from database import DataBase
from dataclass import VKUserData
from vk_api.longpoll import VkEventType

class UserProcessing(object):

    def __init__(self, db: DataBase, api):
        self.db = db
        self.api = api
        self.vkUser = None
        self.request = ''

    def new_vk_user(self, user_id) -> bool:

        if user_id is None:
            return False
        if not self.vkUser is None and self.vkUser.vk_id == user_id:
            return True
        elif self.db.id_in_database(user_id):
            self.vkUser = self.db.get_vkuser(user_id)
        else:
            self.vkUser = VKUserData(self.api.get_info(user_id))
            if not self.db.new_vkuser(self.vkUser):
                return False
        self.get_settings()
        return True

    def get_settings(self):
        if not self.db.get_settings(self.vkUser):
            self.db.set_settings(self.vkUser)

    def get_vk_user(self, vk_id) -> VKUserData:
        vk_user = self.db.get_vkuser(vk_id)
        if vk_user is not None:
            self.db.get_settings(vk_user)
        return vk_user

    def get_list(self, content, _list):
        for l in _list:
            content += f'{self.api.get_user_data(l)[1]}'
        return content

    def update_search_list(self):
        count = 10
        position = self.vkUser.settings.srch_offset
        offset = position + 1
        list = self.api.search(self.vkUser, offset, count)
        self.db.insert_last_search(self.vkUser.vk_id, list, position)

    def get_user(self, user_id):
        user = self.db.get_user(user_id, self.vkUser.settings.srch_offset)
        if user is None:
            self.update_search_list()
            user = self.db.get_user(user_id, self.vkUser.settings.srch_offset)
        print(self.vkUser.settings.srch_offset)
        if user is None:
            return None
        else:
            return user[0]

    def get_next_user(self):
        self.vkUser.settings.srch_offset += 1

        id = self.get_user(self.vkUser.vk_id)

        if id is None:
            return self.get_next_user()
        else:
            if self.db.is_black(self.vkUser.vk_id, id):
                return self.get_next_user()
            else:
                return self.api.get_user_data(id)

    def get_previous_user(self):
        self.vkUser.settings.srch_offset -= 1
        if self.vkUser.settings.srch_offset > 1:
            id = self.get_user(self.vkUser.vk_id)
            print(id)
            if id is None:
                return self.get_previous_user()
            else:
                if self.db.is_black(self.vkUser.vk_id, id):
                    return self.get_previous_user()
                else:
                    return self.api.get_user_data(id)
        else:
            return [None, "не существует"]

    def upd_settings(self):
        self.db.upd_settings(self.vkUser)

    def destruct(self):
        self.vkUser = None

    def add_black_list(self, user_id):
        self.db.new_black_id(user_id, self.get_user(user_id))

    def add_favorite_list(self, user_id):
        self.db.new_favorite(user_id, self.get_user(user_id))

    @staticmethod
    def get_user_id(event):
        if event.type == VkEventType.MESSAGE_NEW:
            user_id = event.object.user_id
        else:
            user_id = None
            print(f'ERROR EVENT {event}')
        return user_id

    @staticmethod
    def get_command_text(event):
        if event.type == VkEventType.MESSAGE_NEW:
            return event.object.payload.get('type')
        else:
            print(f'ERROR EVENT {event}')
            return None

    def run_command(self, command):
        content = ''
        key = command.get('key')
        if not key is None and key != 'none':
            print(f'Запустить команду {key}')
            if key == 'next':
                [command['attachment'], content] = self.get_next_user()
            elif key == 'previous':
                [command['attachment'], content] = self.get_previous_user()
            elif key == 'search':
                [command['attachment'], content] = self.get_next_user()
            elif key == 'black_list':
                content = self.get_list(content, self.db.get_black_list(self.vkUser.vk_id))
            elif key == 'favorites':
                content = self.get_list(content, self.db.get_favorites(self.vkUser.vk_id))
        command['content'] = content
        self.vkUser.settings.last_command = key
        return command

    def get_command(self, event):
        self.request = self.get_command_text(event)
        if event.type == VkEventType.MESSAGE_NEW:
           self.request = self.request.lower()
           c = 'none'
        for c in commands:
            el = commands[c]
            if self.request in el.get('in') or self.request == c:
                break
            command = commands[c]
            return command


