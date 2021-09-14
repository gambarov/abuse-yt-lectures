import re
import asyncio

from service import YTService


def YTDurationToSeconds(duration):
    match = re.match('PT(\d+H)?(\d+M)?(\d+S)?', duration).groups()
    hours = parseInt(match[0]) if match[0] else 0
    minutes = parseInt(match[1]) if match[1] else 0
    seconds = parseInt(match[2]) if match[2] else 0
    return hours * 3600 + minutes * 60 + seconds


def parseInt(string):
    # js-like parseInt
    return int(''.join([x for x in string if x.isdigit()]))


class LectionAbuser():
    def __init__(self, service: YTService) -> None:
        self.service = service

    def run(self, videoIds: list):
        ioloop = asyncio.get_event_loop()
        tasks = []
        # Функция написания и обновления комментария
        async def process(videoId):
            # Получаем длительность видео
            video = await self.service.get_video(videoId)
            # Получаем нужную инфу
            title = video['snippet']['title']
            duration = YTDurationToSeconds(video['contentDetails']['duration'])
            duration = 0
            print(f"Начинаю процесс для видео \"{title}\" ({duration} сек.)")
            # Пишем комментарий
            comment = await self.service.insert_comment(videoId=videoId, text='f1')
            # "Смотрим" видео
            for i in range(1, duration + 5):
                await asyncio.sleep(1)
                print(f"Ожидание {str(i)} сек.")
            # Обновляем комментарий
            await self.service.update_comment(commentId=comment['id'], text='f2')
        # Создаем задачи для всех видео
        for videoId in videoIds:
            tasks.append(ioloop.create_task(process(videoId)))
        # Запускаем и ждем выполнения
        ioloop.run_until_complete(asyncio.wait(tasks))
        ioloop.close()
