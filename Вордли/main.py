import Images

from PASS import PASS

import json
import logging
import random
from texts import *
from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

yandex = Images.YandexImages()
yandex.set_auth_token(token=PASS.token)
yandex.skills = PASS.id
Image = Images.Img()
words = open("words.txt", "r", encoding="UTF8").readlines()
users = set()


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


def handler(event, e):
    user_request = event["request"]["command"]
    user_request = user_request.replace("ё", "е")
    user_request = user_request.replace("-", " ")
    user = event["session"]["user_id"]
    if user not in users:
        users.add(user)
        user_dict = {
            "id": user,
            "name": "",
            "strike": 0,
            "old_words": [],
            "action": "",
            "word": "",
            "Counter": 0
        }
        json.dump(user_dict, open(f'{user}.json', 'w'), indent=4)
    user_dict = json.load(open(f'{user}.json', encoding='utf8'))
    if user_dict["name"] == "":
        if user_dict["action"] == '':
            user_dict["action"] = 'name'
            text = 'Привет! Давай знакомиться, меня зовут Вордл, а тебя?'
        elif user_dict["action"] == 'name':
            user_dict['name'] = user_request.capitalize()
            text = f"Приятно познакомиться, {user_dict['name']}! Знаешь правила игры wordle?"
            user_dict["action"] = 'rules'
        json.dump(user_dict, open(f'{user}.json', 'w'), indent=4)
        return make_response(text=text)
    elif user_dict["action"] == 'rules':
        if yes_or_no(user_request) is None:
            return make_response(text='Не понял тебя, что ты имеешь ввиду?')
        elif yes_or_no(user_request):
            user_dict["action"] = 'start_game'
            json.dump(user_dict, open(f'{user}.json', 'w'), indent=4)
            return make_response(text='Супер! Стартуем?')
        else:
            user_dict["action"] = 'start_game'
            json.dump(user_dict, open(f'{user}.json', 'w'), indent=4)
            return make_response(text=rules + "\nНачинаем играть?")
    elif user_dict["action"] == 'start_game':
        if yes_or_no(user_request) is None:
            return make_response(text='Не понял тебя, что ты имеешь ввиду?')
        elif yes_or_no(user_request):
            user_dict["action"] = 'game'
            json.dump(user_dict, open(f'{user}.json', 'w'), indent=4)
            return game(user_dict)
        else:
            user_dict["action"] = 'exit'
            json.dump(user_dict, open(f'{user}.json', 'w'), indent=4)
            return make_response(text='Жаль, возвращайся ещё..')
    elif user_dict["action"] == 'game':
        return game(user_dict, user_request)


def yes_or_no(answer):
    if answer in Yes_list:
        return True
    elif answer in No_list:
        return False
    else:
        return None


def game(user_dict, answer=''):
    if user_dict['word'] == '':
        user_dict['word'] = words[random.randint(0, len(words))].strip()
        Image.clear()
        yandex.deleteAllImage()
        user_dict["Counter"] = 0
        image_id = yandex.downloadImageFile("Background.png")["id"]
        card = {
            "type": "ImageGallery",
            "items": [
                {
                    "image_id": image_id
                }
            ]
        }
        json.dump(user_dict, open(f'{user_dict["id"]}.json', 'w', encoding='utf8'), indent=4, ensure_ascii=False)
        return make_response(text="Я загадал слово, можешь начинать;)", card=card)
    word = answer
    for i in range(5):
        if word[i] == user_dict["word"][i]:
            Image.fill((0, 204, 0), i, user_dict["Counter"])
        elif word[i] in user_dict["word"]:
            Image.fill((244, 200, 0), i, user_dict["Counter"])
        Image.paster(word[i], i, user_dict["Counter"])
    image_id = yandex.downloadImageFile("Background.png")["id"]
    print(user_dict["word"])
    card = {
        "type": "ImageGallery",
        "items": [
            {
                "image_id": image_id
            }
        ]
    }
    user_dict["Counter"] += 1
    json.dump(user_dict, open(f'{user_dict["id"]}.json', 'w', encoding='utf8'), indent=4, ensure_ascii=False)
    return make_response(text="123", card=card)


if __name__ == '__main__':
    app.run()
