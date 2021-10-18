import time
import datetime
import logging

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait as wait


class YTService:
    def __init__(self, driver: webdriver.Chrome) -> None:
        self.driver = driver

    def auth(self, login: str, password: str):
        try:
            self.driver.get("https://accounts.google.com/signin")

            loginBox = wait(self.driver, 15).until(
                EC.presence_of_element_located((By.NAME, 'identifier')))
            loginBox.send_keys(login)

            self.driver.find_element(By.ID, 'identifierNext').click()

            passwordBox = wait(self.driver, 15).until(
                EC.element_to_be_clickable((By.NAME, 'password')))
            passwordBox.send_keys(password)

            self.driver.find_element(By.ID, 'passwordNext').click()

            # Ждем перенаправления на стр. аккаунта (сразу или после того того, как пользователь пройдет двухфакторку)
            wait(self.driver, 120).until(
                EC.url_contains('https://myaccount.google.com/'))
            return True
        except Exception as e:
            logging.exception(e)
        return False

    def select_channel(self, name: str):
        try:
            self.driver.get('https://www.youtube.com/')
            # Выбираем нужный канал, с которого будем смотреть видео
            accountBtn = wait(self.driver, 15).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//*[contains(text(), '{name}')]"))
            )
            accountBtn.click()
            return True
        except Exception as e:
            logging.exception(e)
        return False

    def get_video_duration(self):
        text = self.driver.find_elements_by_xpath(
            "//span[@class='ytp-time-duration']")[0].text
        duration = time.strptime(text, '%M:%S')
        seconds = datetime.timedelta(
            minutes=duration.tm_min, seconds=duration.tm_sec).total_seconds()
        return int(seconds)

    def insert_comment(self, initComment: str):
        # Кликаем на поле для написания коммента
        commentBox = wait(self.driver, 15).until(
            EC.presence_of_element_located((By.ID, 'placeholder-area')))
        commentBox.click()

        # Печатаем комментарий
        inputBox = wait(self.driver, 15).until(
            EC.presence_of_element_located((By.ID, 'contenteditable-root')))
        inputBox.send_keys(initComment)

        # Отправляем комментарий
        submitBtn = wait(self.driver, 15).until(
            EC.presence_of_element_located((By.ID, 'submit-button')))
        submitBtn.click()
        return True

    def update_comment(self, updComment: str):
        # Раскрываем меню действий (троеточие справа от комментария)
        self.driver.execute_script("document.querySelector('button[aria-label=\"Меню действий\"]').click()")

        # Выбираем пункт с редактированием коммента
        changeBtn = wait(self.driver, 15).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="items"]/ytd-menu-navigation-item-renderer[1]/a')))
        changeBtn.click()

        # Ищем вторые по списку элементы
        # Первые - главные эл-ты для написания нового комментария (которые выше)
        inputBox = self.driver.find_elements_by_id('contenteditable-root')[1]
        inputBox.clear()
        inputBox.send_keys(updComment)

        submitBtn = self.driver.find_elements_by_id('submit-button')[1]
        submitBtn.click()
        return True

    def skip_ad(self):
        # Пытаемся найти кнопку скипа рекламы (если есть, кнопка кликабельна через 5 сек.)
        try:
            skipBtn = wait(self.driver, 15).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="skip-button:6"]/span/button')))
            skipBtn.click()
            return True
        # Реклама не обнаружена
        except TimeoutException as e:
            pass
        except Exception as e:
            logging.exception(e)
        return False
