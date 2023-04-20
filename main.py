import json
from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from Initial_data import community_token, community_id, API_VERSION
from commands import *
from database import *
from keyboard import ClassKeyboard
from user_processing import UserProcessing
from vk_bot import ClassVK


def main():

    token = community_token

    if token is None:
        print('Инициализация бота невозможна!')
        return False
    vk_session = vk_api.VkApi(token=token, api_version=API_VERSION)
    try:
        longpoll = VkLongPoll(vk_session, group_id=community_id)
        vk = vk_session.get_api()
    except Exception as err:
        print('Ошибка инициализации API VK')
        print(err)
        return False
    connection_bot = UserProcessing(DataBase(), ClassVK(community_token))
    print(f"Бот запущен")

    for event in longpoll.listen():
        user_id = connection_bot.get_user_id(event)
        if user_id:
            connection_bot.new_vk_user(user_id)
            command = connection_bot.run_command(command=connection_bot.get_command(event))
            if event.type == VkEventType.MESSAGE_NEW:
                if event.message['text'] != '':
                    if event.from_user:
                        vk.messages.send(
                            user_id=user_id,
                            attachment=command.get('attachment'),
                            random_id=randrange(10 ** 7),
                            peer_id=event.message['from_id'],
                            message=commands.get_answer(command))
            elif event.type == VkEventType.MESSAGE_EVENT:
                if event.get('type') in CALLBACK_TYPES:
                    if event.get('type') == 'show_snackbar':
                        if 'черный' in event.get('text'):
                            connection_bot.add_black_list(event.user_id)
                        elif 'избранное' in event.get('text'):
                            connection_bot.add_favorite_list(event.user_id)

                    vk.messages.sendMessageEventAnswer(
                        event_id=event.event_id,
                        user_id=user_id,
                        peer_id=event.peer_id,
                        event_data=json.dumps(event))
                else:
                    print(command.get('attachment'))
                    vk.messages.send(
                        user_id=user_id,
                        attachment=command.get('attachment'),
                        random_id=randrange(10 ** 7),
                        peer_id=event.peer_id,
                        keyboard=ClassKeyboard.get_keyboard(command['keyboard']),
                        message=ClassKeyboard.get_answer(command))
            else:
                continue
            connection_bot.upd_settings()


if __name__ == '__main__':
    main()

