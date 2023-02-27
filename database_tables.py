from datetime import datetime
from dataclasses import dataclass

vk_user = """CREATE TABLE IF NOT EXISTS vk_user (
                        -- id SERIAL PRIMARY KEY,
                       vk_id INTEGER PRIMARY KEY,
                       first_name VARCHAR(40) NOT NULL,
                       last_name VARCHAR(40),
                       bdate VARCHAR(40),
                       gender INTEGER,
                       city_id INTEGER,
                       city_title VARCHAR(60),
                       vkdomain VARCHAR(100),
                       last_visit VARCHAR(40)
                       );"""

favorites = """CREATE TABLE IF NOT EXISTS favorites ( 
                               vk_id INTEGER NOT NULL,
                               fav_id INTEGER NOT NULL,
                               CONSTRAINT favorites_pk PRIMARY KEY (vk_id, fav_id)
                               );"""


black_list = """CREATE TABLE IF NOT EXISTS black_list (
                                    vk_id INTEGER NOT NULL,
                                    blk_id INTEGER NOT NULL,
                                    CONSTRAINT black_list_pk PRIMARY KEY (vk_id, blk_id)
                                    );"""


last_search = """CREATE TABLE IF NOT EXISTS last_search (
                                  vk_id INTEGER NOT NULL,
                                  lst_id INTEGER NOT NULL,
                                  srch_number INTEGER,
                                  CONSTRAINT last_search_pk PRIMARY KEY (vk_id, lst_id)
                                  );"""

settings = """CREATE TABLE IF NOT EXISTS settings (
                    vk_id INTEGER NOT NULL UNIQUE,
                    access_token VARCHAR (255),
                    srch_offset INTEGER,
                    age_from INTEGER,
                    age_to INTEGER,
                    last_command VARCHAR(100)
                    );"""

CREATE_TABLES = vk_user + favorites + black_list + \
                last_search + settings

drop_vk_user = """DROP TABLE vk_user;"""
drop_favorites = """DROP TABLE favorites;"""
drop_black_list = """DROP TABLE black_list;"""
drop_last_search = """DROP TABLE last_search;"""
drop_settings = """DROP TABLE settings;"""

DROP_TABLES = drop_last_search + drop_favorites + drop_black_list + \
              drop_settings + drop_vk_user

# id "по умолчания" (т.е. не определенный) при создании класса
VK_ID_NOTDEFINED = -1
# settings.srch_offcet - текущая позиция в списке поиска по запросу не задана "по умолчанию"
OFFSET_NOTDEFINED = 0
# границы поиска в настройках пользователя по умолчанию
AGE_FROM_DEFAULT = 20
AGE_TO_DEFAULT = 50

# Пол пользователя ВКонтакте
VK_MALE = 2
VK_FEMALE = 1
VK_UNKNOWN_GENDER = 0

@dataclass
class UserSettings:
    access_token: str
    srch_offset: int
    age_from: int
    age_to: int
    last_command: str


# Класс определяющий набор данных пользователя ВКонтакте
class VKUserData(object):
    # id пользователя ВКонтакте
    vk_id: int = VK_ID_NOTDEFINED
    # Имя пользователя ВКонтакте
    first_name: str = ''
    # Фамилия пользователя
    last_name: str = ''
    # День рождения пользователя
    bdate: str = ''
    # Пол пользоветеля
    gender: int = VK_UNKNOWN_GENDER
    # id города пользователя
    city_id: int = -1
    # Название города пользователя
    city_title: str = ''
    # адрес траницы ВКонтакте пользователя
    vkdomain: str = ''
    # Дата время последнего общения с ботом
    last_visit: str = ''
    # дополнительные свойства пользователя ВКонтакте
    settings: UserSettings

    # инициализация класса
    def __init__(self, *vk_data):
        super().__init__()

        # если никакие аргументы не переданы
        if len(vk_data) == 0:
            # инициализация данных "по умолчанию"
            self.set_default_attrs()
        else:
            if type(vk_data[0]) is list:
                # если заполнение из переданного списка было не корректным
                if not self.set_attr_from_list(vk_data[0]):
                    # то также заполняем параметрами "по умолчанию"
                    self.set_default_attrs()
            elif type(vk_data[0]) is dict:
                if not self.set_attr_from_dict(vk_data[0]):
                    # то также заполняем параметрами "по умолчанию"
                    self.set_default_attrs()
            else:
                # инициализация данных "по умолчанию", если переданн неизвестный набор данных
                self.set_default_attrs()
        # инициализируем дополниетльные параметры класса (settings)
        self.set_default_settings()

    # end __init__()

    # функция заполнения атрибутов класса "по умолчанию"
    def set_default_attrs(self):
        self.vk_id = VK_ID_NOTDEFINED
        self.first_name = ''
        self.last_name = ''
        self.bdate = ''
        self.gender = VK_UNKNOWN_GENDER
        self.city_id = -1
        self.city_title = ''
        self.vkdomain = ''
        self.last_visit = ''
        dt = datetime.now()
        self.last_visit = dt.strftime('%Y-%m-%d %H:%M:%S')

    # end set_default_attrs()

    # функция заполнения "по умолчанию" дополнительных параметров (settings)
    def set_default_settings(self):
        # если у пользователя указана дата рождения то устанавливаем границы поиска по ней
        if len(self.bdate) > 0:
            bdate = datetime.strptime(self.bdate, '%d.%m.%Y')
            age_from = datetime.now() - bdate
            age_from = age_from.days // 365
            age_to = age_from + 1
        else:
            # иначе используем значения по умолчанию
            age_from = AGE_FROM_DEFAULT
            age_to = AGE_TO_DEFAULT

        self.settings = UserSettings(access_token='', srch_offset=OFFSET_NOTDEFINED, age_from=age_from, age_to=age_to,
                                     last_command='')

    # end set_default_settings()

    # проверка, что дополнительные свойства пользователя "пустые" = заполненные значениями по умолчанию
    def settings_empty(self) -> bool:
        result = self.settings.access_token != '' or self.settings.srch_offset != OFFSET_NOTDEFINED or self.settings.age_from != AGE_FROM_DEFAULT or self.settings.age_to != AGE_TO_DEFAULT or self.settings.last_command != ''
        return result
        # end settings_empty()

    # заполнение атрибутов класса (данные) из списка, по порядку
    def set_attr_from_list(self, lst: list) -> bool:
        # проверяем, что переданы все атрибуты (пока без settings)
        if len(lst) != 9:
            return False
        # заполняем атрибуты класса из списка
        self.vk_id = lst[0]
        self.first_name = lst[1]
        self.last_name = lst[2]
        self.bdate = lst[3]
        self.gender = lst[4]
        self.city_id = lst[5]
        self.city_title = lst[6]
        self.vkdomain = lst[7]
        self.last_visit = lst[8]
        dt = datetime.now()
        self.last_visit = dt.strftime('%Y-%m-%d %H:%M:%S')
        return True

    # end set_attr_from_list()

    # заполнение атрибутов класса из словаря vk
    # {'id': int, 'bdate': str, 'city': {'id': int, 'title': str}, 'sex': int,
    #  'screen_name': str, 'first_name': str, 'last_name': str, 'can_access_closed': bool, 'is_closed': bool}
    def set_attr_from_dict(self, vk_dict: dict) -> bool:
        # проверяем, что все необходимые ключи нам переданы
        if 'id' in vk_dict.keys():
            self.vk_id = vk_dict.get('id')
        if 'first_name' in vk_dict.keys():
            self.first_name = vk_dict.get('first_name')
        if 'last_name' in vk_dict.keys():
            self.last_name = vk_dict.get('last_name')
        if 'bdate' in vk_dict.keys():
            self.bdate = vk_dict.get('bdate')
        if 'city' in vk_dict.keys():
            self.city_id = vk_dict.get('city').get('id')
            self.city_title = vk_dict.get('city').get('title')
        if 'sex' in vk_dict.keys():
            self.gender = vk_dict.get('sex')
        if 'screen_name' in vk_dict.keys():
            self.vkdomain = vk_dict.get('screen_name')
        dt = datetime.now()
        self.last_visit = dt.strftime('%Y-%m-%d %H:%M:%S')
        return True

    # end set_attr_from_dict()

    # функция заполнения дополнительных параметров (settings) из списка
    def set_settings_from_list(self, lst: list):
        # если передан полный список ,то заполняем дополнительные свойства
        if len(lst) == 5:
            self.settings = UserSettings(*lst)

    # end set_settings_from_list()

    # функция копирования из другого объекта типа VKUserData
    def copy(self, vk_user):
        self.vk_id = vk_user.vk_id
        self.first_name = vk_user.first_name
        self.last_name = vk_user.last_name
        self.bdate = vk_user.bdate
        self.gender = vk_user.gender
        self.city_id = vk_user.city_id
        self.city_title = vk_user.city_title
        self.vkdomain = vk_user.vkdomain
        self.last_visit = vk_user.last_visit

        self.settings = vk_user.settings
    # end copy()
