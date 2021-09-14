from aiogoogle.client import Aiogoogle
from aiogoogle.models import Response


class YTService:
    def __init__(self, client_creds, user_creds) -> None:
        self.client_creds = client_creds
        self.user_creds = user_creds

    async def insert_comment(self, videoId: str, text: str) -> Response:
        async with Aiogoogle(user_creds=self.user_creds, client_creds=self.client_creds) as aiogoogle:
            youtube = await aiogoogle.discover("youtube", "v3")
            print(f"Отправление комментария {text}...")
            comment = await aiogoogle.as_user(youtube.commentThreads.insert(
                part="snippet",
                json={
                    "snippet": {
                        "videoId": videoId,
                        "topLevelComment": {
                            "snippet": {
                                "textOriginal": text
                            }
                        }
                    }
                }
            ))
            print(f"Комментарий {text} успешно отправлен.")
            return comment

    async def update_comment(self, commentId: str, text: str):
        async with Aiogoogle(user_creds=self.user_creds, client_creds=self.client_creds) as aiogoogle:
            youtube = await aiogoogle.discover("youtube", "v3")
            print(f"Обновление комментария на {text}.")
            response = await aiogoogle.as_user(youtube.comments.update(
                part="snippet",
                json={
                    "id": commentId,
                    "snippet": {
                        "textOriginal": text
                    }
                }
            ))
            print(f"Комментарий успешно обновлен на {text}.")
            return response

    async def get_video(self, videoId: str):
        async with Aiogoogle(user_creds=self.user_creds, client_creds=self.client_creds) as aiogoogle:
            youtube = await aiogoogle.discover("youtube", "v3")
            response = await aiogoogle.as_user(youtube.videos.list(
                part="snippet,contentDetails",
                id=videoId
            ))
            video = response['items'][0]
            return video