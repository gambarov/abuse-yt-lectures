import sys
import json
import asyncio

from abuse.abuser import LectionAbuser
from abuse.service import YTService

import logging

logging.basicConfig(filename='app.log', filemode='w',)

client, user = None, None

# Видео, которые надо заабузить
videoUrls = []

try:
    with open("data/client.json", "r") as json_file:
        client = json.load(json_file)['installed']
    with open("data/user.json", "r") as json_file:
        user = json.load(json_file)
    with open("data/videos.txt", "r") as file:
        videoUrls = [row.strip() for row in file]
    print("Файлы успешно загружены.")
except FileNotFoundError as e:
    print(f"Отсутствует файл {e.filename}.")
    print("Если вы еще не авторизовывались, запустите auth.py.")
    exit()
except Exception as e:
    raise e


def main():
    # Фикс от крит. ошибки в 10 винде
    if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy())
    service = YTService(client_creds=client, user_creds=user)
    abuser = LectionAbuser(service=service)
    abuser.run(videoUrls=videoUrls)


if __name__ == "__main__":
    main()
