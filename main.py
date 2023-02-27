import user_processing
from Initial_data import user_token, community_token, community_id, API_VERSION
import json
from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_bot import ClassVK
from user_processing import UserProcessing
from commands import CALLBACK_TYPES
from modules.db.databases import DataBase
from modules.keyboard.keyboard import ClassKeyboard

# основаная функция программы
def main():
    token = user_token
    if token == None:
        print('Инициализация бота невозможна!')
        return False

    vk_session = VkApi(token=token, api_version=API_VERSION)
    vk = vk_session.get_api()
    try:
        longpoll = VkBotLongPoll(vk_session, group_id=community_id)
    except Exception as err:
        print('Ошибка инициализации API VK')
        print(err)
        return False
    connection_bot = UserProcessing(DataBase(object), ClassVK(community_token))
    print(f"Бот запущен")

    # Основной цикл обработки событий
    for event in longpoll.listen():
        user_id = connection_bot.get_user_id(event)
        if user_id:
            connection_bot.new_vk_user(user_id) #Инициализируем пользователя
            command = connection_bot.run_command(comand=connection_bot.get_comand(event))

if __name__ == '__main__':
    main()
