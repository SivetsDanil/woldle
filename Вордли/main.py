from modes import Images
from PASS import PASS

import json
import logging
import random

from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

yandex = Images.YandexImages()
yandex.set_auth_token(token=PASS.token)
yandex.skills = PASS.id
Image = Images.Img()
f = open("words.txt", "r", encoding="UTF8").readlines()

word = f[random.randint(0, len(f))].strip()


user = {
    "Comp_Word": word,
    "Counter": 0
}


@app.route("/", methods=["POST"])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        "session": request.json["session"],
        "version": request.json["version"],
        "response": {
            "end_session": False
        },
        "application_state": None
    }
    response = handler(request.json, response)
    logging.info(f"Response: {response!r}")
    return json.dumps(response)


def make_response(text=None, card=None, tts=None, buttons=[]):
    response = {
        "response": {
            "text": text,
            "tts": tts,
            "buttons": buttons + [],
            "card": card
        },
        "version": "1.0",
        "application_state": {
            "value": ["", ""]
        },
    }
    return response


def handler(event, context):
    if event["session"]["new"] == True:
        return new()
    request_word = event["request"]["original_utterance"]
    return game(request_word)



def new():
    Image.clear()
    yandex.deleteAllImage()
    user["Counter"] = 0
    x = yandex.downloadImageFile("Background.png")["id"]
    user["Comp_Word"] = f[random.randint(0, len(f))].strip()
    card = {
        "type": "ImageGallery",
        "items": [
            {
                "image_id": x
            }
        ]
    }
    return make_response(text="123", card=card)



def game(word):
    for i in range(5):
        if word[i] == user["Comp_Word"][i]:
            Image.fill((0, 204, 0), i, user["Counter"])
        elif word[i] in user["Comp_Word"]:
            Image.fill((244, 200, 0), i, user["Counter"])
        Image.paster(word[i], i, user["Counter"])
    x = yandex.downloadImageFile("Background.png")["id"]
    print(user["Comp_Word"])
    card = {
        "type": "ImageGallery",
        "items": [
            {
                "image_id": x
            }
        ]
    }
    user["Counter"] += 1
    return make_response(text="123", card=card)



if __name__ == '__main__':
    app.run(debug=True)
