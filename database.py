import psycopg2
from Initial_data import Username, Password, Host, Database
from database_tables import *
from dataclass import *


class DataBase(object):

    def __init__(self):

        self.connection = psycopg2.connect(host=Host,
                                           user=Username,
                                           password=Password,
                                           database=Database)

        self.connection.autocommit = True
        cursor = self.connection.cursor()
        print("Подключение установлено")

        cursor.execute(CREATE_TABLES)

    def get_vkuser(self, vk_id: int) -> VKUserData:
        with self.connection, self.connection.cursor() as cursor:
            query = "SELECT * FROM vk_user WHERE vk_id == vk_id"
            cursor.execute(query, (vk_id,))
            result = cursor.fetchone()
        if result is not None:
            vk_user = VKUserData(list(result))
        else:
            vk_user = None
        return vk_user

    def id_in_database(self, vk_id: int) -> bool:

        if self.get_vkuser(vk_id) is None:
            return False
        return True

    def new_vkuser(self, vk_user: VKUserData) -> bool:
        res = True
        with self.connection, self.connection.cursor() as cursor:
            if not self.id_in_database(vk_user.vk_id):
                query = "INSERT INTO vk_user values( vk_id=vk_user.vk_id," \
                        "first_name=vk_user.first_name," \
                        "last_name=vk_user.last_name," \
                        ")"
                result = cursor.execute(query)
                if result is None:
                    res = False
            return res

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

    def del_last_search_id(self, vk_id: int, lst_id: int) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "DELETE FROM last_seacrh WHERE vk_id == vk_id AND lst_id == lst_id"
            result = cursor.execute(query)
        if result is None:
            return False
        return True

    def get_black_list(self, vk_id: int) -> list:
        with self.connection, self.connection.cursor() as cursor:
            query = "SELECT * FROM black_list.c.blk_id WHERE vk_id == vk_id"
            cursor.execute(query)
            result = cursor.fetchall()
        if result is None or len(result) == 0:
            return list()
        return list.copy(result)

    def del_black_id(self, vk_id: int, blk_id: int) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "DELETE FROM black_list WHERE vk_id == vk_id AND blk_id == blk_id"
            result = cursor.execute(query)
        if result is None:
            return False
        return True

    def get_favorites(self, vk_id: int) -> list:
        with self.connection, self.connection.cursor() as cursor:
            query = "SELECT * FROM favorites.c.fav_id WHERE vk_id == vk_id"
            cursor.execute(query)
            result = cursor.fetchall()
        if result is None or len(result) == 0:
            return list()
        return list.copy(result)

    def new_favorite(self, vk_id: int, fav_id: int) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "SELECT * FROM last_search WHERE vk_id == vk_id AND fav_id == fav_id"
            cursor.execute(query)
            result = cursor.fetchone()
        if result is not None:
            query = "INSERT INTO favorites values( vk_id=vk_id,fav_id=fav_id)"
            cursor.execute(query)
            self.del_last_search_id(vk_id, fav_id)
            self.del_black_id(vk_id, fav_id)
        return True

    def del_favotite(self, vk_id: int, fav_id: int) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "DELETE FROM favorites WHERE vk_id == vk_id AND fav_id == fav_id"
            cursor.execute(query)
        return True

    def del_all_favorites(self, vk_id: int) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "DELETE FROM favorites WHERE vk_id == vk_id"
            cursor.execute(query)
        return True

    def new_black_id(self, vk_id: int, blk_id: int) -> bool:
        with self.connection, self.connection.cursor() as cursor:
          query = "SELECT * FROM black_list WHERE vk_id == vk_id AND blk_id == blk_id"
          cursor.execute(query)
          result = cursor.fetchone()
        if result is not None:
            query = "INSERT INTO black_list values( vk_id=vk_id,blk_id=blk_id)"
            cursor.execute(query)
            self.del_last_search_id(vk_id, blk_id)
            self.del_black_id(vk_id, blk_id)
        return True

    def del_all_last_search(self, vk_id: int) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "DELETE FROM last_search WHERE vk_id == vk_id"
            cursor.execute(query)
        return True

    def del_black_list(self, vk_id: int) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "DELETE FROM black_list WHERE vk_id == vk_id"
            cursor.execute(query)
        return True

    def is_black(self, vk_id: int, blk_id: int) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "SELECT * FROM black_list WHERE vk_id == vk_id AND blk_id == blk_id"
            cursor.execute(query)
            result = cursor.fetchone()
        if result is None:
            return False
        else:
            return True

    def get_settings(self, vk_user: VKUserData) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "SELECT * FROM settings WHERE vk_id == vk_id"
            cursor.execute(query)
            result = cursor.fetchone()
        if result is None:
            return False
        else:
            vk_user.set_settings_from_list(list(result)[1:])
            return True

    def get_user(self, user_id, srch_number):
        with self.connection, self.connection.cursor() as cursor:
            query = "SELECT * FROM last_search.c.lst_id WHERE vk_id == user_id AND srch_number == srch_number"
            cursor.execute(query)
            result = cursor.fetchone()
        return result

    def set_settings(self, vk_user: VKUserData) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "INSERT INTO settings values( vk_id=vk_user.vk_id," \
                        "srch_offset=vk_user.settings.srch_offset," \
                        "age_from=vk_user.settings.age_from," \
                        "age_to=vk_user.settings.age_to," \
                        ")"
            cursor.execute(query)
        return True

    def upd_settings(self, vk_user: VKUserData) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            query = "UPDATE settings SET values WHERE vk_id == vk.user.vk_id"
            result = cursor.execute(query, (vk_user.vk_id,))
        if result is None:
            return False
        return True

