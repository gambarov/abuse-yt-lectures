import time

from abuse.utils import get_video_duration

import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LectureAbuser():
    def __init__(self) -> None:
        pass

    def run(self, driver: webdriver.Chrome, videoUrls: list, config):
        if (len(videoUrls)) == 0:
            print('Список видео пустой. Добавьте видео и перезапустите скрипт.')
            return

        driver.maximize_window()

        login = config.get('Account', 'Login')
        password = config.get('Account', 'Password')
        channelName = config.get('Account', 'ChannelName')

        if not self._auth(driver, login, password, channelName):
            print('Не удалось авторизоваться, попробуйте еще раз.')
            return

        time.sleep(1)

        initComment = config.get('General', 'InitComment')
        updComment = config.get('General', 'UpdComment')

        for videoUrl in videoUrls:
            if not self._process_video(driver, videoUrl, initComment, updComment):
                print(f'Не удалось обработать видео {videoUrl}.')

    def _auth(self, driver: webdriver.Chrome, login, password, channelName):
        try:
            driver.get("https://accounts.google.com/signin")

            loginBox = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, 'identifier')))
            loginBox.send_keys(login)

            driver.find_element(By.ID, 'identifierNext').click()

            passwordBox = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.NAME, 'password')))
            passwordBox.send_keys(password)

            driver.find_element(By.ID, 'passwordNext').click()

            # Ждем перенаправления на стр. аккаунта (сразу или после того того, как пользователь пройдет двухфакторку)
            WebDriverWait(driver, 15).until(
                EC.url_contains('https://myaccount.google.com/'))

            driver.get('https://www.youtube.com/')

            # Выбираем нужный канал, с которого будем смотреть видео
            accountBtn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//*[contains(text(), '{channelName}')]"))
            )
            accountBtn.click()
            return True
        except Exception as e:
            logging.exception(e)
        return False

    def _process_video(self, driver, videoUrl, initComment, updComment):
        try:
            print(f'Открываю видео {videoUrl}...')
            driver.get(videoUrl)

            WebDriverWait(driver, 15).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="container"]/h1')))

            driver.execute_script("window.scrollBy(0,600)")

            commentBox = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, 'placeholder-area')))
            commentBox.click()

            print(f'Пишу начальный комментарий "{initComment}"...')
            inputBox = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, 'contenteditable-root')))
            inputBox.send_keys(initComment)

            submitBtn = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, 'submit-button')))
            submitBtn.click()

            duration = get_video_duration(driver)
            print(f'Ожидаю {duration} секунд...')

            time.sleep(duration)
            driver.execute_script("window.scrollBy(0,300)")

            # Раскрываем меню действий (троеточие справа от комментария)
            driver.execute_script(
                """isClicked=false;
                    els=document.querySelectorAll('#button');
                    els.forEach((el)=>{
                        if(el.ariaLabel=='Меню действий'&&isClicked==false){
                            el.click();
                            isClicked=true
                        }
                    })""")

            changeBtn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="items"]/ytd-menu-navigation-item-renderer[1]/a')))
            changeBtn.click()

            print(f'Обновляю комментарий на "{updComment}"...')

            # Ищем вторые по списку элементы 
            # Первые - главные эл-ты для написания нового комментария (которые выше)

            inputBox = driver.find_elements_by_id('contenteditable-root')[1]
            inputBox.clear()
            inputBox.send_keys(updComment)

            submitBtn = driver.find_elements_by_id('submit-button')[1]
            submitBtn.click()

            time.sleep(0.5)

            # Отмечаем свой просмотр на сайте пердуна
            videoId = videoUrl.replace(
                'https://www.youtube.com/watch?v=', '', 1)
            driver.get(f"http://hsm.ugatu.su/yt/wtload.php?videoId={videoId}")
            time.sleep(0.25)
            logging.info(f'Success for {videoUrl}')
            return True
        except Exception as e:
            logging.exception(e)
        return False
