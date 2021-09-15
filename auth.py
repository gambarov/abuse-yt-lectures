#!/usr/bin/python3.7

import sys
import webbrowser

from sanic import Sanic, response
from sanic.exceptions import ServerError

from aiogoogle import Aiogoogle
from aiogoogle.auth.utils import create_secret

import json

sys.path.append("../..")

client, user = None, None

try:
    with open("data/client.json", "r") as json_file:
        client = json.load(json_file)['installed']
except FileNotFoundError:
    print("Отсутствует файл client.json.")
except Exception as e:
    raise e

try:
    with open("data/user.json", "r") as json_file:
        user = json.load(json_file)
        print("Файла с польз. данными успешно создан, можете запустить start.py.")
        exit()
except FileNotFoundError:
    print("Файла с польз. данными не обнаружено.")
except Exception as e:
    raise e

SCOPES = ['https://www.googleapis.com/auth/youtube',
          'https://www.googleapis.com/auth/youtube.force-ssl']
CLIENT_CREDS = {
    "client_id": client["client_id"],
    "client_secret": client["client_secret"],
    "scopes": SCOPES,
    "redirect_uri": "http://localhost:5000/callback/aiogoogle",
}
state = create_secret()  # Shouldn't be a global hardcoded variable.


LOCAL_ADDRESS = "localhost"
LOCAL_PORT = "5000"

app = Sanic(__name__)
aiogoogle = Aiogoogle(client_creds=CLIENT_CREDS)


@app.route("/authorize")
def authorize(request):
    if aiogoogle.oauth2.is_ready(CLIENT_CREDS):
        uri = aiogoogle.oauth2.authorization_url(
            client_creds=CLIENT_CREDS,
            state=state,
            access_type="offline",
            include_granted_scopes=True,
            prompt="select_account",
        )
        return response.redirect(uri)
    else:
        raise ServerError(
            "Нет необходимых данных для авторизации (проверьте наличие файла client.json).")


@app.route("/callback/aiogoogle")
async def callback(request):
    if request.args.get("error"):
        error = {
            "error": request.args.get("error"),
            "error_description": request.args.get("error_description"),
        }
        return response.json(error)
    elif request.args.get("code"):
        returned_state = request.args["state"][0]
        # Check state
        if returned_state != state:
            raise ServerError("NO")
        # Step D & E (D send grant code, E receive token info)
        user = await aiogoogle.oauth2.build_user_creds(
            grant=request.args.get("code"), client_creds=CLIENT_CREDS
        )
        with open('data/user.json', "w") as json_file:
            json_file.write(json.dumps(user))
        return response.text("Авторизация прошла успешно, можете запустить start.py для начала работы.")
    else:
        # Should either receive a code or an error
        return response.text("Что-то пошло не так.")


def main():
    # Первичная авторизация
    if not user:
        webbrowser.open("http://" + LOCAL_ADDRESS +
                        ":" + LOCAL_PORT + "/authorize")
        app.run(host=LOCAL_ADDRESS, port=LOCAL_PORT, debug=True)
    else:
        # Сервер более не нужен
        if app.is_running:
            app.stop()


if __name__ == "__main__":
    main()
