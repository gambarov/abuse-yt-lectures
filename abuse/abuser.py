import time

from abuse.service import YTService

import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
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

        print('Авторизация...')

        if not self.service.auth(config.get('Account', 'Login'), config.get('Account', 'Password')):
            print('Не удалось авторизоваться, попробуйте еще раз.')
            return

        print('Выбор канала...')

        if not self.service.select_channel(config.get('Account', 'ChannelName')):
            print('Не удалось выбрать канал YouTube, убедитесь что в названии канала нет ошибок')
            return

        time.sleep(1)

        for videoUrl in videoUrls:
            if not self.process_video(videoUrl,
                    config.get('General', 'InitComment'),
                    config.get('General', 'UpdComment')):
                print(f'Не удалось обработать видео {videoUrl}.')
                return
            else:
                print(f'Успешно обработано видео {videoUrl}')
        return True

    def process_video(self, videoUrl: str, initComment: str, updComment: str, delay: float = None):
        try:
            print(f'Открытие видео {videoUrl}...')

            self.driver.get(videoUrl)

            # Ждем загрузки страницы
            title = wait(self.driver, 15).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="container"]/h1')))

            # Пропуск возможной рекламы
            if self.service.skip_ad():
                print('Реклама обнаружена, пропуск...')

            # Получаем длительность видео, если нужно
            # ВНИМАНИЕ: получить длительность нужно обязательно после пропуска рекламы!
            if delay is None:
                delay = self.service.get_video_duration()

            # Проматываем вниз, чтобы открыть комменты
            self.driver.execute_script("arguments[0].scrollIntoView();", title)

            if self.service.insert_comment(initComment):
                print(f'Написан начальный комментарий "{initComment}".')

            print(f'Ожидание {delay} секунд...')
            time.sleep(delay / 2)
            # Останавливаем видео на половине
            # Если остановить в начале, то гугл может посчитать за спам
            self.driver.execute_script(
                "document.getElementsByClassName('ytp-large-play-button')[0].click()")
            time.sleep((delay / 2) + 2.5)

            # Перед обновлением снова проматываем, на всякий случай
            self.driver.execute_script("arguments[0].scrollIntoView();", title)

            if self.service.update_comment(updComment):
                print(f'Комментарий обновлен на "{updComment}".')

            time.sleep(1)

            print(f'Регистрация просмотра на сайте...')

            # Отмечаем свой просмотр на сайте пердуна
            videoId = videoUrl.replace(
                'https://www.youtube.com/watch?v=', '', 1)
            self.driver.get(
                f"http://hsm.ugatu.su/yt/wtload.php?videoId={videoId}")

            time.sleep(1)

            logging.info(f'Success for {videoUrl}')
            return True
        except Exception as e:
            logging.exception(e)
        return False
