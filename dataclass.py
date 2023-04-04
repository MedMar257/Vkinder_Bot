from dataclasses import dataclass
from datetime import datetime


VK_ID_NOTDEFINED = -1
OFFSET_NOTDEFINED = 0
AGE_FROM_DEFAULT = 18
AGE_TO_DEFAULT = 50

VK_MALE = 2
VK_FEMALE = 1
VK_UNKNOWN_GENDER = 0


@dataclass
class UserSettings:
    srch_offset: int
    age_from: int
    age_to: int


class VKUserData(object):
    vk_id: int = VK_ID_NOTDEFINED
    first_name: str = ''
    last_name: str = ''
    bdate: str = ''
    gender: int = VK_UNKNOWN_GENDER
    city_id: int = -1
    city_title: str = ''
    settings: UserSettings

    def __init__(self, *vk_data):
        super().__init__()

        if len(vk_data) == 0:
            self.set_default_attrs()
        else:
            if type(vk_data[0]) is list:
                if not self.set_attr_from_list(vk_data[0]):
                    self.set_default_attrs()
            elif type(vk_data[0]) is dict:
                if not self.set_attr_from_dict(vk_data[0]):
                    self.set_default_attrs()
            else:
                self.set_default_attrs()
        self.set_default_settings()

    def set_default_attrs(self):
        self.vk_id = VK_ID_NOTDEFINED
        self.first_name = ''
        self.last_name = ''
        self.bdate = ''
        self.gender = VK_UNKNOWN_GENDER
        self.city_id = -1
        self.city_title = ''

    def set_default_settings(self):
        if len(self.bdate) > 0:
            bdate = datetime.strptime(self.bdate, '%d.%m.%Y')
            age_from = datetime.now() - bdate
            age_from = age_from.days // 365
            age_to = age_from + 1
        else:
            age_from = AGE_FROM_DEFAULT
            age_to = AGE_TO_DEFAULT

        self.settings = UserSettings(srch_offset=OFFSET_NOTDEFINED, age_from=age_from, age_to=age_to)

    def settings_empty(self) -> bool:
        result = self.settings.srch_offset != OFFSET_NOTDEFINED or self.settings.age_from != AGE_FROM_DEFAULT or self.settings.age_to != AGE_TO_DEFAULT
        return result

    def set_attr_from_list(self, lst: list) -> bool:
        if len(lst) != 6:
            return False
        self.vk_id = lst[0]
        self.first_name = lst[1]
        self.last_name = lst[2]
        self.bdate = lst[3]
        self.gender = lst[4]
        self.city_id = lst[5]
        self.city_title = lst[6]
        return True

    def set_attr_from_dict(self, vk_dict: dict) -> bool:
        if 'id' in vk_dict.keys():
            self.vk_id = vk_dict.get('id')
        if 'first_name' in vk_dict.keys():
            self.first_name = vk_dict.get('first_name')
        if 'last_name' in vk_dict.keys():
            self.last_name = vk_dict.get('last_name')
        return True

    def set_settings_from_list(self, lst: list):
        if len(lst) == 3:
            self.settings = UserSettings(*lst)

    def copy(self, vk_user):
        self.vk_id = vk_user.vk_id
        self.first_name = vk_user.first_name
        self.last_name = vk_user.last_name
        self.bdate = vk_user.bdate
        self.gender = vk_user.gender
        self.city_id = vk_user.city_id
        self.city_title = vk_user.city_title
        self.settings = vk_user.settings