# -*- coding: utf-8 -*-

import psycopg2
from Initial_data import Username, Password, Host, Database
from database_tables import *
from dataclass import *
from peewee import *


conn_db = PostgresqlDatabase(Database, user=Username, password=Password, host=Host)

class BaseModel(Model):

    class Meta:
        database = conn_db


class vk_user(BaseModel):
    id = IntegerField(primary_key=True)
    vk_id = IntegerField(primary_key=True)
    first_name = CharField(null=False)
    last_name = CharField(null=True)


class favorites(BaseModel):
    vk_id = IntegerField(null=False)
    fav_id = IntegerField(null=False)
    primary_key = CompositeKey('vk_id', 'fav_id')


class black_list(BaseModel):
    vk_id = IntegerField(null=False)
    blk_id = IntegerField(null=False)
    black_list_pk = CompositeKey('vk_id', 'blk_id')


class last_search(BaseModel):
    vk_id = IntegerField(null=False)
    lst_id = IntegerField(null=False)
    srch_number = IntegerField(null=True)
    last_search_pk = CompositeKey('vk_id', 'lst_id')


class settings(BaseModel):
    vk_id = IntegerField(null=False)
    age_from = IntegerField(null=True)
    age_to = IntegerField(null=True)


def get_vkuser(vk_id: int) -> VKUserData:
    if not vk_user.table_exists():
        vk_user.create_table()
    try:
        vk_users = vk_user.get().where(vk_id=vk_id)
        return VKUserData(list[vk_users])
    except:
        return None


def id_in_database(vk_id: int) -> bool:
    if get_vkuser(vk_id) is None:
        return False
    return True


def new_vkuser(vk_user_data: VKUserData) -> bool:
    if not vk_user.table_exists():
        vk_user.create_table()
    try:
        vk_user_model = vk_user(vk_id=vk_user_data.vk_id, first_name=vk_user_data.first_name, last_name=vk_user_data.last_name)
        vk_user_model.save()
        return True
    except:
        return False


def insert_last_search(user_id, lst_ids, position):
    if not last_search.table_exists():
        last_search.create_table()
    result = True
    try:
        for lst_id in lst_ids:
            if not last_search.get_or_none(vk_id=user_id, lst_id=lst_id):
                last_search_model = last_search(vk_id=user_id, lst_id=lst_id, srch_number=position)
                last_search_model.save()
                position += 1
        return result
    except:
        return False

def del_last_search_id(vk_id: int, lst_id: int) -> bool:
    if not last_search.table_exists():
        last_search.create_table()
    try:
        last_search_model = last_search.get().where(vk_id=vk_id, lst_id=lst_id)
        last_search_model.delete_instance()
        return True
    except:
        return False


def get_black_list(vk_id: int) -> list:
    if not black_list.table_exists():
        black_list.create_table()
    try:
        result = black_list.select().where(black_list.vk_id == vk_id)
        return [row.blk_id for row in result]
    except:
        return list()


def del_black_id(vk_id: int, blk_id: int) -> bool:
    if not black_list.table_exists():
        black_list.create_table()
    try:
        black_list_model = black_list.get(vk_id=vk_id, blk_id=blk_id)
        black_list_model.delete_instance()
        return True
    except:
        return False

def get_favorites(vk_id: int) -> list:
    if not favorites.table_exists():
        favorites.create_table()
    try:
        result = favorites.select().where(favorites.vk_id == vk_id)
        return [row.fav_id for row in result]
    except:
        return list()


def new_favorite(vk_id: int, fav_id: int) -> bool:
    if not black_list.table_exists():
        black_list.create_table()
    if not last_search.table_exists():
        last_search.create_table()
    if not favorites.table_exists():
        favorites.create_table()
    try:
        if black_list.get(vk_id=vk_id, blk_id=fav_id):
            black_list.delete().where(black_list.vk_id==vk_id, black_list.blk_id==fav_id).execute()
        if last_search.get(vk_id=vk_id, search_id=fav_id):
            last_search.delete().where(last_search.vk_id==vk_id, last_search.search_id==fav_id).execute()
        new_fav = favorites(vk_id=vk_id, fav_id=fav_id)
        new_fav.save()
        return True
    except:
        return False


def del_favorite(vk_id: int, fav_id: int) -> bool:
    if not favorites.table_exists():
        favorites.create_table()
    try:
        favorites.delete().where(favorites.vk_id==vk_id, favorites.fav_id==fav_id).execute()
        return True
    except:
        return False

def del_all_favorites(vk_id: int) -> bool:
    if not favorites.table_exists():
        favorites.create_table()
    try:
        favorites.delete().where(favorites.vk_id==vk_id).execute()
        return True
    except:
        return False

def new_black_id(vk_id: int, blk_id: int) -> bool:
    if not last_search.table_exists():
        last_search.create_table()
    if not black_list.table_exists():
        black_list.create_table()
    try:
        if last_search.get(vk_id=vk_id, search_id=blk_id):
            last_search.delete().where(last_search.vk_id==vk_id, last_search.search_id==blk_id).execute()
        if black_list.get(vk_id=vk_id, blk_id=blk_id):
            return False
        new_black_list_row = black_list(vk_id=vk_id, blk_id=blk_id)
        new_black_list_row.save()
        return True
    except:
        return False

def del_all_last_search(vk_id: int) -> bool:
    if not last_search.table_exists():
        last_search.create_table()
    try:
        last_search.delete().where(last_search.vk_id==vk_id).execute()
        return True
    except:
        return False

def del_black_list(vk_id: int) -> bool:
    if not black_list.table_exists():
        black_list.create_table()
    try:
        black_list.delete().where(black_list.vk_id==vk_id).execute()
        return True
    except:
        return False

def is_black(vk_id: int, blk_id: int) -> bool:
    if not black_list.table_exists():
        black_list.create_table()
    try:
        black_list.get(vk_id=vk_id, blk_id=blk_id)
        return True
    except:
        return False

def get_settings(vk_user_data: VKUserData) -> bool:
    if not settings.table_exists():
        settings.create_table()
    try:
        settings_row = settings.get(settings.vk_id == vk_user_data.vk_id)
        vk_user.set_settings_from_list([settings_row.srch_offset,
                                        settings_row.age_from,
                                        settings_row.age_to])
        return True
    except:
        return False

def get_user(user_id: int, srch_number: int):  # что тут должно возвращаться?
    if not last_search.table_exists():
        last_search.create_table()
    try:
        lst_row = last_search.get((last_search.vk_id == user_id) & (last_search.search_id == srch_number))
        return lst_row
    except:
        return None

def set_settings(vk_user_data: VKUserData) -> bool:
    if not settings.table_exists():
        settings.create_table()
    try:
        settings.create(vk_id=vk_user_data.vk_id,
                        srch_offset=vk_user_data.settings.srch_offset,
                        age_from=vk_user_data.settings.age_from,
                        age_to=vk_user_data.settings.age_to)
        return True
    except:
        return False

def upd_settings(vk_user_data: VKUserData) -> bool:
    if not settings.table_exists():
        settings.create_table()
    try:
        settings.update(srch_offset=vk_user_data.settings.srch_offset,
                        age_from=vk_user_data.settings.age_from,
                        age_to=vk_user_data.settings.age_to).where(settings.vk_id==vk_user_data.vk_id).execute()
        return True
    except:
        return False

