import requests
import json
import time
from datetime import datetime
from pprint import pprint
from tqdm import tqdm


Token_vk =""
user_id_vk = 134442214
Yandex_token = ""

def progress(target,times):#Мини анимация прогресса
    for i in tqdm(target):
        time.sleep(times)


class VK:
    url_base_vk = "https://api.vk.ru/method/"

    def __init__(self, access_token, user_id, version='5.199'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.photo = {}

    def photos_get(self):
        """Метод достает информацию о фото со странице вк"""
        PARAMS={
            "owner_id" : self.id,
            "access_token" : self.token,
            "album_id" : 'profile',
            "extended" : 1,
            "v" : self.version
        }
        result = requests.get(self.url_base_vk + "photos.get", params=PARAMS).json()
        result = result["response"]["items"]
        for photos in result:
            if "sizes" in photos:
                for sizes_photo in photos["sizes"]:
                    if "z" ==  sizes_photo["type"]:
                        for_progress = self.photo[(datetime.utcfromtimestamp(photos["date"])).strftime("%Y.%m.%d")] = sizes_photo["url"]
                        progress(for_progress,0.01)
        return f"На странице id{self.id}, {len(self.photo)} фото."
    
class YANDEX_DISK(VK):
    url_base_ya = "https://cloud-api.yandex.net/"

    def __init__(self,qauth_token):
        self.token = qauth_token

    def create_folder(self,name_folders):
        """Создание папки"""
        url_metod = "v1/disk/resources"
        params = {
            "path" : f'{name_folders}'
        }
        header = { "Authorization" : f'OAuth {self.token}' }
        response = requests.put((self.url_base_ya + url_metod),params=params,headers=header)
        if 200 <= response.status_code < 300:
            return f"Папка '{name_folders}' создана"
        else:
            return f"Возникла ошибка {response.status_code}"
    
    def loading_photo(self,vk_id,name_folders,photo_date):
        """Метод загружающий в папку яндекс диска фото по дате фото из вк"""
        url_metod = "v1/disk/resources/upload"
        url_photo = f'{vk_id.photo[photo_date]}'
        header = { "Authorization" : f'OAuth {self.token}' }
        response = requests.get(url_photo)
        if response.status_code == 200:
            file = {"file" : response.content}
            params = {
            "path" : f'{name_folders}/{photo_date}.jpg'
            }
            response = requests.get((self.url_base_ya + url_metod),params=params,headers=header)
            upload_params = response.json()
            progress(upload_params,0.1)
            try:
                response = requests.put(upload_params['href'],files=file)
            except KeyError:
                return "Это фото уже загружено"    
            return "Фото загружено в папку"
        else:
            return "Возникла ошибка"

    
my_vk = VK(Token_vk,user_id_vk)
print(my_vk.photos_get())

my_ya_disk = YANDEX_DISK(Yandex_token)
print(my_ya_disk.create_folder("Папка для фото"))


print(my_ya_disk.loading_photo(my_vk,"Папка для фото",'2019.05.30'))
print(my_ya_disk.loading_photo(my_vk,"Папка для фото",'2020.12.23'))
print(my_ya_disk.loading_photo(my_vk,"Папка для фото",'2018.03.26'))
