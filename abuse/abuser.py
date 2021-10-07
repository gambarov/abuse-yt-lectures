import sys
import re
import asyncio

from abuse.service import YTService

import logging

import webbrowser

from pprint import pformat

import requests

def YTDurationToSeconds(duration):
    match = re.match('PT(\d+H)?(\d+M)?(\d+S)?', duration).groups()
    hours = parseInt(match[0]) if match[0] else 0
    minutes = parseInt(match[1]) if match[1] else 0
    seconds = parseInt(match[2]) if match[2] else 0
    return hours * 3600 + minutes * 60 + seconds


def parseInt(string):
    # js-like parseInt
    return int(''.join([x for x in string if x.isdigit()]))


def parseVideoId(url):
    return url.replace('https://www.youtube.com/watch?v=', '', 1)


class LectureAbuser():
    def __init__(self, service: YTService) -> None:
        self.service = service

    def run(self, videoUrls: list, initComment: str, updComment: str, openVideoOnError: bool):
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
            tasks.append(ioloop.create_task(self.handle(
                index, videoId, initComment, updComment, openVideoOnError)))
            index = index + 1
        # Запускаем и ждем выполнения
        ioloop.run_until_complete(asyncio.wait(tasks))
        ioloop.close()

    async def handle(self, index, videoId, initComment: str, updComment: str, openVideoOnError: bool = False):
        index = str(index)
        try:
            video = await self.__tryGetVideoData(index, videoId)
            title = video['snippet']['title']
            print(f"[{index}]: Начат процесс для видео \"{title}\".")
            comment = await self.__tryInsertComment(index, videoId, initComment)
            duration = YTDurationToSeconds(video['contentDetails']['duration']) + 5
            print(f"[{index}]: Ожидание {duration} сек.")
            await asyncio.sleep(1)
            response = await self.__tryUpdateComment(index, comment['id'], videoId, updComment, openVideoOnError)
            if response:
                requests.get(f"http://hsm.ugatu.su/yt/wtload.php?videoId={videoId}")
            print(f"[{index}]: Процесс успешно завершен.")
        except Exception as e:
            print(f"[{index}]: Процесс завершился с ошибкой.")
            logging.exception(e)

    async def __tryGetVideoData(self, index, videoId):
        try:
            video = await self.service.get_video(videoId)
            return video
        except Exception as e:
            print(f"[{index}]: Не удалось получить данные о видео.")
            logging.exception(e)
            return False

    async def __tryInsertComment(self, index, videoId, text):
        try:
            print(f"[{index}]: Отправление комментария...")
            comment = await self.service.insert_comment(videoId=videoId, text=text)
            print(f"[{index}]: Комментарий успешно отправлен.")
            logging.info(f"Message sended, response body:\n{pformat(comment)}")
            return comment
        except Exception as e:
            print(f"[{index}]: Не удалось отправить комментарий.")
            logging.exception(e)
            return False

    async def __tryUpdateComment(self, index, commentId, videoId, text, openVideoOnError=False):
        try:
            print(f"[{index}]: Обновление комментария...")
            response = await self.service.update_comment(commentId=commentId, text=text)
            print(f"[{index}]: Комментарий успешно обновлен.")
            return response
        except Exception as e:
            print(
                f"[{index}]: Не удалось обновить комментарий, попробуйте сделать это самостоятельно.")
            logging.exception(e)
            if openVideoOnError:
                webbrowser.open(
                    url=f"https://www.youtube.com/watch?v={videoId}")
            return False