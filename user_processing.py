from commands import commands
from database import DataBase
from vk_api.bot_longpoll import VkBotEventType
from database_tables import VKUserData


class UserProcessing(object):

    # функция инициализации класса
    def __init__(self, db: DataBase, api):
        self.db = db
        self.api = api
        self.vkUser = None
        self.request = ''

    # функция обновления информации о пользователе начавшем диалог с ВКБотом
    # функция вызывается ВКБотом при начале диалога пользователя
    # возвращае True, если данные сохранены, иначе False
    def new_vk_user(self, user_id) -> bool:

        if user_id is None:
            return False

        if not self.vkUser is None and self.vkUser.vk_id == user_id:
            # Пишет тот же пользователь, vkUser не меняется
            return True
        elif self.db.id_in_database(user_id):  # нет такого пользователя в базе данных
            # Получим пользователя из БД
            self.vkUser = self.db.get_vkuser(user_id)
            self.db.vk_user_update_last_visit(self.vkUser)
        else:
            # Создадим пользователя
            self.vkUser = VKUserData(self.api.get_info(user_id))
            # создаем или обновляем (если существует) данные о пользователе
            if not self.db.new_vkuser(self.vkUser):
                return False
        # Проверим свойства в БД и сохраним, если их нет там
        self.get_settings()
        return True

    # end new_vk_user

    # Получить информацию о пользователе по его id
    # возвращается объект VKUserData или None если нет записей в базе данных
    def get_vk_user(self, vk_id) -> VKUserData:
        # запрашиваем базу данных
        vk_user = self.db.get_vkuser(vk_id)
        # если пользователь записан в базу данных
        if vk_user is not None:
            # считываем дополнительные настройки пользователя из базы данных
            self.db.get_setings(vk_user)
        return vk_user

    def get_list(self, content, _list):
        for l in _list:
            content += f'{self.api.get_user_data(l)[1]}'
        return content

    def run_command(self, comand):
        content = ''
        key = comand.get('key')
        if not key is None and key != 'none':
            print(f'Запустить команду {key}')
            if key == 'next':
                [comand['attachment'], content] = self.get_next_user()
            elif key == 'previous':
                [comand['attachment'], content] = self.get_previous_user()
            elif key == 'search':
                [comand['attachment'], content] = self.get_next_user()
            elif key == 'black_list':
                content = self.get_list(content, self.db.get_black_list(self.vkUser.vk_id))
            elif key == 'favorites':
                content = self.get_list(content, self.db.get_favorites(self.vkUser.vk_id))
            elif key == 'save_token':
                if self.api.check_token(self.vkUser.vk_id, self.request):
                    self.vkUser.settings.access_token = self.request
                    content = "Токен сохранен"
                else:
                    content = f"Токен не правильный: {self.request}"
        comand['content'] = content
        self.vkUser.settings.last_command = key
        return comand

    def update_search_list(self):
        count = 10  # Размер пакета данных
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

    # Следующий обрабатываемый пользователь
    def get_next_user(self):
        self.vkUser.settings.srch_offset += 1

        id = self.get_user(self.vkUser.vk_id)

        if id is None:
            return self.get_next_user()
        else:
            if self.db.is_black(self.vkUser.vk_id, id) == True:
                return self.get_next_user()
            else:
                return self.api.get_user_data(id)

    # Предыдущий обрабатываемый пользователь
    def get_previous_user(self):
        self.vkUser.settings.srch_offset -= 1
        if self.vkUser.settings.srch_offset > 1:
            id = self.get_user(self.vkUser.vk_id)
            print(id)
            if id is None:
                return self.get_previous_user()
            else:
                if self.db.is_black(self.vkUser.vk_id, id) == True:
                    return self.get_previous_user()
                else:
                    return self.api.get_user_data(id)
        else:
            return [None, "не существует"]

    def upd_settings(self):
        self.db.upd_setings(self.vkUser)

    def destruct(self):
        self.vkUser = None

    @staticmethod
    def get_user_id(event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message['from_id']
        elif event.type == VkBotEventType.MESSAGE_EVENT:
            user_id = event.object.user_id
        elif event.type == VkBotEventType.MESSAGE_REPLY:
            user_id = None
        else:
            user_id = None
            print(f'ERROR EVENT {event}')
        return user_id

    @staticmethod
    def get_command_text(event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            return event.obj.message['text']
        elif event.type == VkBotEventType.MESSAGE_EVENT:
            return event.object.payload.get('type')
        elif event.type == VkBotEventType.MESSAGE_REPLY:
            return None
        else:
            print(f'ERROR EVENT {event}')
            return None

    # считать дополнительные данные о пользователе из базы данных
    def get_settings(self):
        if not self.db.get_setings(self.vkUser):
            # сохраняем исходные данные в базе данных
            self.db.set_setings(self.vkUser)

    # end get_setings_smart()

    def add_black_list(self, user_id):
        self.db.new_black_id(user_id, self.get_user(user_id))

    def add_favorite_list(self, user_id):
        self.db.new_favorite(user_id, self.get_user(user_id))

    def get_comand(self, event):
        self.request = self.get_command_text(event)
        if event.type == VkBotEventType.MESSAGE_NEW:
            if self.vkUser.settings.last_command == 'set_token':
                return commands['save_token']

        self.request = self.request.lower()
        c = 'none'
        for c in commands:
            el = commands[c]
            if self.request in el.get('in') or self.request == c:
                break
        command = commands[c]
        return command

