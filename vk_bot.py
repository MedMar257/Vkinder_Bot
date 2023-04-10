from pprint import pprint
import time
from urllib import response
import requests
from Initial_data import API_VERSION, API_URL, user_token
from dataclass import VKUserData


class ClassVK(object):

    def __init__(self, access_token=user_token):
        self.access_token = access_token
        self.API_URL = API_URL

    def get_info(self, user_ids):
        method = 'users.get'
        print(method, user_ids)
        url = self.API_URL + method
        params = {
            'user_ids': user_ids,
            'access_token': self.access_token,
            'fields': 'screen_name, city, bdate, sex',
            'v': API_VERSION
        }

        res = self.get_vk_data(url, params)
        response = res.json().get("response")

        if response:
            return response[0]
        else:
            return None

    def get_photo(self, owner_id: str, count=3):
        method = 'photos.get'
        url = self.API_URL + method
        params = {
            'owner_id': owner_id,
            'album_id': 'profile',
            'access_token': self.access_token,
            'extended': 1,
            'count': count,
            'v': API_VERSION
        }
        res = self.get_vk_data(url, params)
        res = res.json()

        if res.get('error') is not None:
            print(res['error']['error_msg'])
        return res

    def get_user_data(self, id):
        attachments = []
        content = ''
        if id != 0:
            params = self.get_info(id)

            if params:
                city = bdata = ""
                if params.get('city'):
                    city = params.get('city').get('title')
                if params.get('bdate'):
                    bdata = params.get('bdate')
                content = f'\n[id{id}|{params.get("first_name")} {params.get("last_name")}] {city} {bdata}'
                photos = self.get_photo(id, 3)
                if photos.get('response') is not None:
                    items = photos['response']['items']
                    for item in items:
                        attachments.append(f'photo{id}_{item.get("id")}')
        return [','.join(attachments), content]

    def users_search(self, vk_user: VKUserData, count=1, offset=0):
        method = 'users.search'
        pprint(vk_user.settings)
        pprint(vk_user.city_id)
        url = self.API_URL + method
        ids = []
        params = dict(count=count, city=vk_user.city_id, offset=offset,
                      age_from=vk_user.settings.age_from, age_to=vk_user.settings.age_to,
                      sex=self.sex_invert(vk_user.gender), v=API_VERSION, has_photo=1,
                      status=6, sort=0)
        print(method, params)
        res = self.get_vk_data(url, params)
        res.json().get("res")
        return res

    def search(self, vk_user: VKUserData, offset, count):
        search_list = self.users_search(vk_user, count=count, offset=offset)
        return search_list

    @staticmethod
    def sex_invert(sex):
        if sex == 1:
            sex = 2
        elif sex == 2:
            sex = 1
        else:
            sex = 0
        return sex

    @staticmethod
    def get_vk_data(url, params) -> response:
        resp = ''
        repeat = True
        while repeat:
            resp = requests.get(url, params=params)
            data = resp.json()
            if 'error' in data and 'error_code' in data['error'] and data['error']['error_code'] == 6:
                time.sleep(2)
            else:
                repeat = False
        return resp