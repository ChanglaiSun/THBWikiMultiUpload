import requests
import os
from urllib.parse import quote

S = requests.Session()
URL = "https://thwiki.cc/api.php"


def read_bot_token():
    """
    using local token file, you need to make a BotToken.txt file
    the token file should like
    """

    """
        botusername=XXXXX
        botpassword=XXXXX
    """

    f = open(r"BotToken.txt", "r", encoding="utf-8")

    bot_token = {}

    for line in f.readlines():
        name, value = line.strip("\n").split("=", 1)
        bot_token[name] = value
    return bot_token


def fetch_login_token():
    """ Fetch login token via `tokens` module """

    response = S.get(url=URL, params={
        "action": "query",
        "meta": "tokens",
        "type": "login",
        "format": "json"
    })

    data = response.json()

    return data["query"]["tokens"]["logintoken"]


def start_client_login(username, password):
    """
    Send a post request along with login token, user information
    and return URL to the API to log in on a wiki
    """

    login_token = fetch_login_token()

    response = S.post(url=URL, data={
        "action": "clientlogin",
        "username": username,
        "password": password,
        "loginreturnurl": "http://127.0.0.1:5000/",
        "logintoken": login_token,
        "format": "json"
    })

    data = response.json()

    if data["clientlogin"]["status"] == "PASS":
        print("Clientlogin Success")
    else:
        print("Clientlogin Failed")


def start_bot_login(botusername, botpassword):
    """
    using BotPasswords to login with API access
    """

    login_token = fetch_login_token()

    response = S.post(url=URL, data={
        "action": "login",
        "lgname": botusername,
        "lgpassword": botpassword,
        "lgtoken": login_token,
        "format": "json"
    })

    data = response.json()

    if data["login"]["result"] == "Success":
        print("Login Success")
    else:
        print("Login Failed")

    return


def retrieve_csrf_token():
    """retrieve Csrf token after login"""

    response = S.get(url=URL, params={
        "action": "query",
        "meta": "tokens",
        "format": "json"
    })

    data = response.json()

    return data["query"]["tokens"]["csrftoken"]


def upload_file(filepath, filename, csrftoken, comment=""):
    """FILE DIC
    ("filename", "fileobject", "content-type", "headers")
    """
    encoded_filename = quote(filename)

    # FILE = {"file":("红黑月历.png",open(filepath,"rb"),"multipart/form-data")}
    file = {"file": (encoded_filename, open(filepath, "rb"), "multipart/form-data")}

    response = S.post(url=URL, files=file, data={
        "action": "upload",
        "filename": filename,
        "format": "json",
        "token": csrftoken,
        "comment": comment,
        "ignorewarnings": 1
    })

    data = response.json()

    if data["upload"]["result"] == "Success":
        print("Upload {name} Success".format(name=filename))
    else:
        print("Upload {name} failed".format(name=filename))

    return


def multi_upload(path, csrftoken, comment=""):
    os.chdir(path)
    files = os.listdir(path)

    for f in files:
        upload_file(f, f, csrftoken, comment)

    return


BOT_TOKEN = read_bot_token()
start_bot_login(BOT_TOKEN["botusername"], BOT_TOKEN["botpassword"])
CSRF_TOKEN = retrieve_csrf_token()  # CSRF_TOKEN can use for many times

# upload_file(FILE_PATH,"2020-03-27-3.png",CSRF_TOKEN)

PATH = input("Please input directory path:\n")
COMMENT = input("Please input upload comment(support wikitext) within single line:\n")
multi_upload(PATH, CSRF_TOKEN, COMMENT)
