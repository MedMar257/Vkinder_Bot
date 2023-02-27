import psycopg2
from Initial_data import Username, Password, Host, Database
from database_tables import *


class DataBase(object):

    def __init__(self):

        self.connection = psycopg2.connect(host=Host,
                                           user=Username,
                                           password=Password,
                                           database=Database)

        self.connection.autocommit = True
        cursor = self.connection.cursor()
        print("Подключение установлено")

        # создаем таблицы в Базе данных, только если они не существуют
        cursor.execute(CREATE_TABLES)

        # функция получения данных пользователя ВКонтакте из базы данных
        # возвращает объект типа VKUserData или None, если запрос неудачный (нет данных)

    def get_vkuser(self, vk_id: int) -> VKUserData:
        # формируем заброс к базе данных
        with self.connection, self.connection.cursor() as cursor:
            query = "SELECT * FROM vk_user WHERE vk_id == vk_id"
            cursor.execute(query, (vk_id,))
            result = cursor.fetchone()
        # заполняем и возвращаем объект VKUserData
        if result is not None:
            vk_user = VKUserData(list(result))
        else:
            vk_user = None
        return vk_user
        # end get_vkuser()

    # функция проверки, есть ли пользователь в базе данных
    def id_in_database(self, vk_id: int) -> bool:

        if self.get_vkuser(vk_id) is None:
            return False
        return True

    # end id_in_database()

    # обновляем время последнего общения с ботом у существующего в базе пользователя
    def vk_user_update_last_visit(self, vk_user: VKUserData) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "UPDATE vk_user SET last_vizit WHERE vk_id == vk.user.vk_id"
            result = cursor.execute(query, (vk_user.vk_id,))
        # если запрос выполнился с ошибкой
        if result is None:
            return False
        # успешный результат
        return True
        # end vk_user_update_last_visit()

        # функция сохранения данных о пользователе ВКонтакте в базу данных
        # возвращае True, если данные сохранены в базе данных, иначе False

    def new_vkuser(self, vk_user: VKUserData) -> bool:
        res = True
        with self.connection, self.connection.cursor() as cursor:
            if not self.id_in_database(vk_user.vk_id):
                # нет такого пользователя в базе данных
                query = "INSERT INTO vk_user values( vk_id=vk_user.vk_id," \
                        "first_name=vk_user.first_name," \
                        "last_name=vk_user.last_name," \
                        "bdate=vk_user.bdate," \
                        "gender=vk_user.gender," \
                        "city_id=vk_user.city_id," \
                        "city_title=vk_user.city_title," \
                        "vkdomain=vk_user.vkdomain," \
                        "last_visit=vk_user.last_visit" \
                        ")"
                result = cursor.execute(query)
                if result is None:
                    res = False
            else:
                result = self.vk_user_update_last_visit(vk_user)
                if result is None:
                    res = False
            return res
        # enf new_vk_user()

    # Вставить массив данных в last_search
    def insert_last_search(self, user_id, lst_ids, position):
        with self.connection, self.connection.cursor() as cursor:
            for lst_id in lst_ids:
                query = "SELECT * FROM last_search WHERE vk_id == user_id AND lst_id == lst_id"
                cursor.execute(query)
                result = cursor.fetchone()
                if result is not None:
                    continue
                query = "INSERT INTO last_search values( " \
                        "vk_id=user_id," \
                        "lst_id=lst_id," \
                        "srch_number=position" \
                        ")"
                result = cursor.execute(query)
                position += 1
            return result

    # удалить контакт из списка поиска
    def del_last_search_id(self, vk_id: int, lst_id: int) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "DELETE FROM last_seacrh WHERE vk_id == vk_id AND lst_id == lst_id"
            result = cursor.execute(query)
        if result is None:
            return False
        # успешный результат
        return True

    # удалить контакт из заблокированных
    def del_black_id(self, vk_id: int, blk_id: int) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "DELETE FROM black_list WHERE vk_id == vk_id AND blk_id == blk_id"
            result = cursor.execute(query)
        if result is None:
            return False
        # успешный результат
        return True

    # end del_black_id()

    # сохранить в базе данных информацию об избранном контакте
    def new_favorite(self, vk_id: int, fav_id: int) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "SELECT * FROM last_search WHERE vk_id == vk_id AND fav_id == fav_id"
            cursor.execute(query)
            result = cursor.fetchone()
        if result is not None:
            query = "INSERT INTO favorites values( vk_id=vk_id,fav_id=fav_id)"
            cursor.execute(query)
            # удаляем id из списка поиска
            self.del_last_search_id(vk_id, fav_id)
            # удаляем id из черного списка
            self.del_black_id(vk_id, fav_id)
        return True

    # end new_favorite()

    # получить список избранных
    def get_favorites(self, vk_id: int) -> list:
        with self.connection, self.connection.cursor() as cursor:
            query = "SELECT * FROM favorites.c.fav_id WHERE vk_id == vk_id"
            cursor.execute(query)
            result = cursor.fetchall()
        # если записей нет, то возвращаем пустой список
        if result is None or len(result) == 0:
            return list()
        # возвращаем список fav_id
        return list.copy(result)
    # end get_favorites()

    # удалить избранный контакт у пользовалетя из базы данных
    def del_favotite(self, vk_id: int, fav_id: int) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "DELETE FROM favorites WHERE vk_id == vk_id AND fav_id == fav_id"
            cursor.execute(query)
        return True
    # end del_favorite()

    # удалить все избранные контакты пользователя
    def del_all_favorites(self, vk_id: int) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "DELETE FROM favorites WHERE vk_id == vk_id"
            cursor.execute(query)
        return True
    # end del_all_favorites()

    # получить список заблокированных контактов
    def get_black_list(self, vk_id: int) -> list:
        with self.connection, self.connection.cursor() as cursor:
            query = "SELECT * FROM black_list.c.blk_id WHERE vk_id == vk_id"
            cursor.execute(query)
            result = cursor.fetchall()
        # если записей нет, то возвращаем пустой список
        if result is None or len(result) == 0:
            return list()
        # разбиваем список из пары vk_id, fav_id и получаем list(fav_id)
        return list.copy(result)
    # end get_black_list()

    # сохранить заблокированный контакт
    def new_black_id(self, vk_id: int, blk_id: int) -> bool:
        with self.connection, self.connection.cursor() as cursor:
          query = "SELECT * FROM black_list WHERE vk_id == vk_id AND blk_id == blk_id"
          cursor.execute(query)
          result = cursor.fetchone()
        if result is not None:
            query = "INSERT INTO black_list values( vk_id=vk_id,blk_id=blk_id)"
            cursor.execute(query)
        # удаляем id из списка поиска
            self.del_last_search_id(vk_id, blk_id)
        # удаляем id из списка фаворитов
            self.del_black_id(vk_id, blk_id)
        return True
        # если есть то записей в базу данных не делаем

    # end new_black_id()

    # удалить контакт из списка поиска
    def del_all_last_search(self, vk_id: int) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "DELETE FROM last_search WHERE vk_id == vk_id"
            cursor.execute(query)
        return True
    # end del_all_last_search()

    # удалить весь "блэк лист" пользователя
    def del_black_list(self, vk_id: int) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "DELETE FROM black_list WHERE vk_id == vk_id"
            cursor.execute(query)
        return True
    # end del_black_list

    # проверка ID пользователя на включенеи в черный список
    def is_black(self, vk_id: int, blk_id: int) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "SELECT * FROM black_list WHERE vk_id == vk_id AND blk_id == blk_id"
            cursor.execute(query)
            result = cursor.fetchone()
        if result is None:
            return False
        else:
            return True
    # end is_black()

    # считать дополнительные данные о пользователе из базы данных
    def get_setings(self, vk_user: VKUserData) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "SELECT * FROM settings WHERE vk_id == vk_id"
            cursor.execute(query)
            result = cursor.fetchone()
        if result is None:
            return False
        else:
            vk_user.set_settings_from_list(list(result)[1:])
            return True
    # end get_settings()

    # получить из базы "наденного" по номеру смещения
    def get_user(self, user_id, srch_number):
        with self.connection, self.connection.cursor() as cursor:
            query = "SELECT * FROM last_search.c.lst_id WHERE vk_id == user_id AND srch_number == srch_number"
            cursor.execute(query)
            result = cursor.fetchone()
        return result
    # get_user()

    # сохранение дополнительных параметров пользователя в базе данных
    def set_setings(self, vk_user: VKUserData) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "INSERT INTO settings values( vk_id=vk_user.vk_id," \
                        "access_token=vk_user.settings.access_token," \
                        "srch_offset=vk_user.settings.srch_offset," \
                        "age_from=vk_user.settings.age_from," \
                        "age_to=vk_user.settings.age_to," \
                        "last_command=vk_user.settings.last_command" \
                        ")"
            cursor.execute(query)
        return True
    # end set_settins()

    # обновить данные параметров пользователя в базе данных
    def upd_setings(self, vk_user: VKUserData) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "UPDATE settings SET values WHERE vk_id == vk.user.vk_id"
            result = cursor.execute(query, (vk_user.vk_id,))
        # если запрос выполнился с ошибкой
        if result is None:
            return False
        # успешный результат
        return True
