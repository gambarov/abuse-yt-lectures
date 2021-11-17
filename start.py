import os

import logging
import configparser
import argparse

from abuse.abuser import LectureAbuser

import undetected_chromedriver.v2 as uc


logging.basicConfig(filename='logs/app.log', level=logging.INFO)

config = configparser.ConfigParser()

parser = argparse.ArgumentParser()
parser.add_argument('--headless', action='store_true')

args = parser.parse_args()

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
    with uc.Chrome(version_main=95, headless=args.headless) as driver:
        abuser = LectureAbuser(driver)
        abuser.run(
            videoUrls=videoUrls,
            login=config.get('Account', 'Login'),
            password=config.get('Account', 'Password'),
            channelName=config.get('Account', 'ChannelName'),
            initComment=config.get('General', 'InitComment'),
            updComment=config.get('General', 'UpdComment'),
            ignoreOnError=config.getboolean('General', 'IgnoreOnError')
        )

    os.system("pause")


if __name__ == "__main__":
    main()
