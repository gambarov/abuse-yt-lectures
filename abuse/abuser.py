import time

from .service import YTService

import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC


class LectureAbuser():
    def __init__(self, driver: webdriver.Chrome) -> None:
        self.service = YTService(driver)
        self.driver = driver

    def run(
        self,
        videoUrls: list,
        login: str,
        password: str,
        channelName: str,
        initComment: str,
        updComment: str,
        ignoreOnError: bool = False
    ):
        if (len(videoUrls)) == 0:
            print('Список видео пустой. Добавьте видео и перезапустите скрипт.')
            return

        self.driver.maximize_window()

        print('Авторизация...')

        if not self.service.auth(login, password):
            print('Не удалось авторизоваться, попробуйте еще раз.')
            return False

        print('Выбор канала...')

        if not self.service.select_channel(channelName):
            print('Не удалось выбрать канал YouTube')
            return False

        time.sleep(1)

        for videoUrl in videoUrls:
            if not self.process_video(videoUrl, initComment, updComment):
                print(f'Не удалось обработать видео {videoUrl}.')
                self.driver.get_screenshot_as_file(f"logs/errors/{videoUrl}.png")
                if not ignoreOnError:
                    return False
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
                # В случае неуспеха пытаемся снова
                if delay is None:
                    print('Не удалось получить длительность видео, новая попытка...')
                    return self.process_video(videoUrl, initComment, updComment)

            # Проматываем вниз, чтобы открыть комменты
            self.driver.execute_script("arguments[0].scrollIntoView();", title)

            if not self.service.insert_comment(initComment):
                print(f'Не удалось написать комментарий.')
                return False
            else:
                print(f'Написан начальный комментарий "{initComment}".')

            print(f'Ожидание {delay} секунд...')

            self.service.wait_with_actions(delay)

            # Перед обновлением снова проматываем, на всякий случай
            self.driver.execute_script("arguments[0].scrollIntoView();", title)

            if not self.service.update_comment(updComment):
                print(f'Не удалось обновить комментарий.')
                return False
            else:
                print(f'Комментарий обновлен на "{updComment}".')

            time.sleep(1)

            print(f'Регистрация просмотра на сайте...')

            # Отмечаем просмотр на сайте
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
