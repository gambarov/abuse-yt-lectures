import os

import logging
import configparser
import argparse

from abuse.abuser import LectureAbuser

import undetected_chromedriver.v2 as uc


logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO)

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
    with uc.Chrome(headless=args.headless) as driver:
        abuser = LectureAbuser(driver)
        # В случае ошибки делаем скриншот
        if not abuser.run(videoUrls=videoUrls, config=config):
            driver.get_screenshot_as_file("error.png")

    os.system("pause")


if __name__ == "__main__":
    main()
