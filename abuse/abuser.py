import sys
import re
import asyncio

from abuse.service import YTService

import logging


def YTDurationToSeconds(duration):
    match = re.match('PT(\d+H)?(\d+M)?(\d+S)?', duration).groups()
    hours = parseInt(match[0]) if match[0] else 0
    minutes = parseInt(match[1]) if match[1] else 0
    seconds = parseInt(match[2]) if match[2] else 0
    return hours * 3600 + minutes * 60 + seconds


def parseInt(string):
    # js-like parseInt
    return int(''.join([x for x in string if x.isdigit()]))


def parseVideoId(string):
    return string.replace('https://www.youtube.com/watch?v=', '', 1)


class LectionAbuser():
    def __init__(self, service: YTService) -> None:
        self.service = service

    def run(self, videoUrls: list):
        if (len(videoUrls)) == 0:
            print('Список видео пустой. Добавьте видео и перезапустите скрипт.')
            return

        if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy())

        ioloop = asyncio.get_event_loop()
        tasks = []
        # Создаем задачи для всех видео
        index = 1
        for url in videoUrls:
            videoId = parseVideoId(url)
            tasks.append(ioloop.create_task(self.handle(index, videoId)))
            index = index + 1
        # Запускаем и ждем выполнения
        ioloop.run_until_complete(asyncio.wait(tasks))
        ioloop.close()

    # Функция написания и обновления комментария
    async def handle(self, index, videoId):
        index = str(index)
        # Получаем данные о видео
        try:
            video = await self.service.get_video(videoId)
        except Exception as e:
            print(
                f"[{index}]: Не удалось начать процесс для видео {videoId} (не удалось получить данные о видео).")
            logging.exception(e)
            return
        # Вытаскиваем нужную инфу (название, длительность)
        title = video['snippet']['title']
        duration = YTDurationToSeconds(
            video['contentDetails']['duration']) + 5
        duration = 0
        print(
            f"[{index}]: Начат процесс для видео \"{title}\" (ID = {videoId}).")

        # Пишем комментарий
        try:
            print(f"[{index}]: Отправление комментария...")
            comment = await self.service.insert_comment(videoId=videoId, text='f1')
        except Exception as e:
            print(f"[{index}]: Не удалось отправить комментарий.")
            logging.exception(e)
            return
        print(f"[{index}]: Комментарий успешно отправлен.")
        print(f"[{index}]: Ожидание {duration} сек.")

        # "Смотрим" видео
        await asyncio.sleep(duration + 5)
        # Обновляем комментарий
        try:
            print(f"[{index}]: Обновление комментария...")
            await self.service.update_comment(commentId=comment['id'], text='f2')
        except Exception as e:
            print(f"[{index}]: Не удалось обновить комментарий.")
            logging.exception(e)
            return
        print(f"[{index}]: Комментарий успешно обновлен.")
        print(f"[{index}]: Успешно завершен процесс для видео \"{title}\".")
