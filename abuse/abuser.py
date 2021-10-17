import time

from abuse.service import YTService

import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LectureAbuser():
    def __init__(self, driver: webdriver.Chrome) -> None:
        self.service = YTService(driver)
        self.driver = driver

    def run(self, videoUrls: list, config):
        if (len(videoUrls)) == 0:
            print('Список видео пустой. Добавьте видео и перезапустите скрипт.')
            return

        self.driver.maximize_window()

        login = config.get('Account', 'Login')
        password = config.get('Account', 'Password')
        channelName = config.get('Account', 'ChannelName')

        if not self.service.auth(login, password, channelName):
            print('Не удалось авторизоваться, попробуйте еще раз.')
            return

        time.sleep(1)

        initComment = config.get('General', 'InitComment')
        updComment = config.get('General', 'UpdComment')

        for videoUrl in videoUrls:
            if not self.process_video(videoUrl, initComment, updComment):
                print(f'Не удалось обработать видео {videoUrl}.')
                time.sleep(1000)

    def process_video(self, videoUrl, initComment, updComment):
        try:
            print(f'Открытие видео {videoUrl}...')
            self.driver.get(videoUrl)

            # Ждем загрузки страницы
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="container"]/h1')))

            # Пропуск возможной рекламы
            if self.service.skip_ad():
                print('Реклама обнаружена, пропуск...')

            # Проматываем вниз, чтобы открыть комменты
            self.driver.execute_script("window.scrollBy(0,600)")

            if self.service.insert_comment(initComment):
                print(f'Написан начальный комментарий "{initComment}".')

            duration = self.service.get_video_duration()
            print(f'Ожидание {duration} секунд...')
            time.sleep(duration / 2)
            # Останавливаем видео на половине
            # Если остановить в начале, то гугл может посчитать за спам
            self.driver.execute_script(
                "document.getElementsByClassName('ytp-large-play-button')[0].click()")
            time.sleep(duration / 2 + 5)

            self.driver.execute_script("window.scrollBy(0,300)")

            if self.service.update_comment(updComment):
                print(f'Комментарий обновлен на "{updComment}".')

            time.sleep(1)

            # Отмечаем свой просмотр на сайте пердуна
            videoId = videoUrl.replace(
                'https://www.youtube.com/watch?v=', '', 1)
            self.driver.get(f"http://hsm.ugatu.su/yt/wtload.php?videoId={videoId}")

            time.sleep(1)

            logging.info(f'Success for {videoUrl}')
            print(f'Успешно просмотрено видео {videoUrl}')
            return True
        except Exception as e:
            logging.exception(e)
        return False
