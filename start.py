import os

import logging
import configparser

from abuse.abuser import LectureAbuser

import undetected_chromedriver.v2 as uc

logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO)

config = configparser.ConfigParser()

# Видео, которые надо заабузить
videoUrls = []

try:
    # Настройки
    config.read("config.ini", encoding="utf-8")
    # Список видео
    with open("data/videos.txt", "r") as file:
        videoUrls = [row.strip() for row in file]
    print("Файлы успешно загружены.")
except FileNotFoundError as e:
    print(f"Отсутствует файл {e.filename}.")
    exit()
except Exception as e:
    raise e


def main():
    abuser = LectureAbuser()

    with uc.Chrome() as driver:
        abuser.run(driver=driver, videoUrls=videoUrls, config=config)

    os.system("pause")


if __name__ == "__main__":
    main()
