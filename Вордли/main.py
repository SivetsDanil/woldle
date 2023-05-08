import Images

from PASS import PASS

import json
import logging
import random
import os
from texts import *
from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

yandex = Images.YandexImages()
yandex.set_auth_token(token=PASS.token)
yandex.skills = PASS.id
Image = Images.Img()




rus_words_5 = open("words.txt", "r", encoding="UTF8").readlines()[0].strip().split()



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


def make_response(text="null", card=None, tts=None, buttons=[], end=False, user_dict={}):
    if user_dict != {}:
        json.dump(user_dict, open(f'{user_dict["id"]}.json', 'w', encoding='utf8'), indent=4, ensure_ascii=False)
    response = {
        "response": {
            "end_session": end,
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
    user_request = event["request"]["command"].lower()
    user_request = user_request.replace("ё", "е")
    user_request = user_request.replace("-", " ")
    user = event["session"]["user_id"]
    if event["session"]["new"] and not os.path.isfile(user):
        try:
            user_dict = json.load(open(f'{user}.json', encoding='utf8'))
            if user_dict["action"] == 'name':
                text = 'И снова здравствуй! Я так и не знаю твое имя:(\nСкажи, как тебя зовут?'
                return make_response(text=text, user_dict=user_dict)
            return menu(user_dict)
        except FileNotFoundError:
            user_dict = {"id": user, "name": "", "strike": 0, "old_words": [], "action": 'name', "word": "",
                         "Counter": 0, "language": "русский", "lange": 5, "level": "начинающий", "change_action": ''}
            text = 'Привет! Давай знакомиться, меня зовут Вордл, а тебя?'
            return make_response(text=text, user_dict=user_dict)
    user_dict = json.load(open(f'{user}.json', encoding='utf8'))
    if user_dict["action"] == "name":
        user_dict["name"] = user_request.capitalize()
        user_dict["action"] = "menu"
        return menu(user_dict)
    if user_dict["action"] == "changes":
        return changing(user_dict, user_request)
    if user_request == 'настройки' or user_dict["action"] == "settings":
        if user_dict["name"] == '':
            user_dict["action"] = "name"
            return make_response(text=f'Пожалуйста, скажи свое имя, а то незнакомцам я с настройками не помогаю...', user_dict=user_dict)
        user_dict["action"] = 'changes'
        return settings(user_dict)
    if user_request == 'начать игру':
        return game(user_dict=user_dict)
    if user_dict["action"] == 'game':
        return game(user_dict=user_dict, answer=user_request)
    if user_dict["action"] == "menu":
        return menu(user_dict)

def yes_or_no(answer):
    if answer in Yes_list:
        return True
    elif answer in No_list:
        return False
    else:
        return None


def changing(user_dict, user_request):
    if user_request == 'выйти':
        user_dict["action"] = "menu"
        return menu(user_dict)
    elif user_request == 'смена имени':
        user_dict["change_action"] = 'change_name'
        return make_response(text='Скажи мне, как тебя теперь называть?', user_dict=user_dict)
    elif user_dict["change_action"] == 'change_name':
        user_dict["action"] = 'settings'
        user_dict["name"] = user_request.capitalize()
        user_dict["change_action"] = ""
        return make_response(text=f'Теперь буду звать тебя {user_request.capitalize()};)', user_dict=user_dict)
    elif user_request == 'смена длины':
        user_dict["change_action"] = 'change_lange'
        return make_response(text='Скажи, какой длины от 3 до 6 букв давать слова?', user_dict=user_dict)
    elif user_dict["change_action"] == 'change_lange':
        if "три" in user_request or "3" in user_request:
            user_dict["lange"] = 3
        elif "чет" in user_request or "4" in user_request:
            user_dict["lange"] = 4
        elif "пят" in user_request or "5" in user_request:
            user_dict["lange"] = 5
        elif "шест" in user_request or "6" in user_request:
            user_dict["lange"] = 6
        else:
            return make_response(text=f'Я тебя не понял, пожалуйста, сказажи иначе...\nНа всякий случай, я даю слова от 3 до 6 букв', user_dict=user_dict)
        user_dict["action"] = 'settings'
        user_dict["change_action"] = ""
        return make_response(text=f'Теперь буду загадывать слова по {user_request} букв.', user_dict=user_dict)
    elif user_request == 'смена сложности':
        user_dict["change_action"] = 'change_level'
        card = {
            "type": "ItemsList",
            "header": {
                "text": "Выбери подходящий уровень сложности"
            },
            "items": levels,
        }
        buttons = [{"title": "Выйти", "hide": False}]
        return make_response(card=card, buttons=buttons, user_dict=user_dict)
    elif user_dict["change_action"] == 'change_level':
        if user_request not in ['начинающий', 'продвинутый', 'эрудит']:
            return make_response(text='Пожалуйста, выбери один из представленных или используй кнопки..', user_dict=user_dict)
        user_dict["action"] = 'settings'
        user_dict["level"] = user_request
        user_dict["change_action"] = ""
        return make_response(text=f'Теперь буду загадывать слова для уровня "{user_request.capitalize()}".', user_dict=user_dict)
    elif user_request == 'смена языка':
        user_dict["change_action"] = 'change_language'
        return make_response(text='Какой язык выберешь: русский или английский?', user_dict=user_dict)
    elif user_dict["change_action"] == 'change_language':
        if 'рус' in user_request or "rus" in user_request:
            user_dict["language"] = 'русский'
            user_dict["action"] = 'settings'
            user_dict["change_action"] = ""
            return make_response(text=f'Теперь буду загадывать слова из русского языка.', user_dict=user_dict)
        elif "анг" in user_request or "eng" in user_request:
            user_dict["language"] = 'английский'
            user_dict["action"] = 'settings'
            user_dict["change_action"] = ""
            return make_response(text=f'Теперь буду загадывать слова из английского языка.', user_dict=user_dict)
        else:
            return make_response(text=f'Я тебя не понял, пожалуйста, сказажи иначе...', user_dict=user_dict)
    else:
        user_dict["action"] = 'settings'

def settings(user_dict):
    settings = [
        {
            "image_id": "1652229/3d093b89fdaebbf80b62",
            "title": "Сменить твоё имя",
            "description": f"Сейчас: {user_dict['name']}.",
            "button": {"text": "Смена имени"}
        },
        {
            "image_id": "1652229/3d093b89fdaebbf80b62",
            "title": "Изменить длину слов",
            "description": f"Сейчас: {user_dict['lange']}.",
            "button": {"text": "Смена длины"}
        },
        {
            "image_id": "1652229/3d093b89fdaebbf80b62",
            "title": "Поменять сложность игры",
            "description": f"Сейчас твой уровень - {user_dict['level']}.",
            "button": {"text": "Смена сложности"}
        },
        {
            "image_id": "1652229/3d093b89fdaebbf80b62",
            "title": "Сменить язык слов",
            "description": f"Сейчас я загадываю на языке: {user_dict['language']}.",
            "button": {"text": "Смена языка"}
        }
    ]
    card = {
        "type": "ItemsList",
        "header": {
            "text": "Итак, ты в настройках."
        },
        "items": settings,
    }
    text = "Ты в настройках, выбери что хочешь изменить."
    buttons = [{"title": "Выйти", "hide": False}]
    user_dict["action"] = "changes"
    return make_response(text=text, card=card, buttons=buttons, user_dict=user_dict)


def menu(user):
    card = {
        "type": "ItemsList",
        "header": {
            "text": f'Добро пожаловать, {user["name"]}!'
        },
        "items": start_menu
    }
    return make_response(text=f'Привет, {user["name"]}!', card=card, user_dict=user)


def game(user_dict, answer=''):
    user_dict["action"] = "game"
    if user_dict['word'] == '' or answer == '':
        user_dict['word'] = random.choice(list(set(rus_words_5) - set(user_dict["old_words"]))).strip()
        user_dict['word'].replace('ё', "е")
        Image.clear()
        yandex.deleteAllImage()
        user_dict["Counter"] = 0
        image_id = yandex.downloadImageFile("Background.png")["id"]
        card = {
            "type": "ImageGallery",
            "items": [
                {
                    "image_id": image_id,
                    "title": "Я загадал слово, можешь начинать;)"
                }
            ]
        }

        json.dump(user_dict, open(f'{user_dict["id"]}.json', 'w', encoding='utf8'), indent=4, ensure_ascii=False)
        return make_response(text="123", card=card, user_dict=user_dict)
    word = answer
    if len(word) != user_dict["lange"]:
        return make_response(text=f'Я жду от тебя слова длиной в {user_dict["lange"]} букв, можешь сменить режим в настройках.', user_dict=user_dict)
    elif word not in rus_words_5:
        return make_response(
            text=f'Я не знаю такое слово, давай другое:(\nНапоминаю, мы используем только существительные', user_dict=user_dict)
    for i in range(user_dict["lange"]):
        if word[i] == user_dict["word"][i] or word[i] == '':
            Image.fill((0, 204, 0), i, user_dict["Counter"])
        elif word[i] in user_dict["word"]:
            Image.fill((244, 200, 0), i, user_dict["Counter"])
        Image.paster(word[i], i, user_dict["Counter"])
    image_id = yandex.downloadImageFile("Background.png")["id"]
    card = {
        "type": "ImageGallery",
        "items": [
            {
                "image_id": image_id,
                "title": "TEST TEST TEST"
            }
        ]
    }
    user_dict["Counter"] += 1
    json.dump(user_dict, open(f'{user_dict["id"]}.json', 'w', encoding='utf8'), indent=4, ensure_ascii=False)
    return make_response(text="123", card=card, user_dict=user_dict)


if __name__ == '__main__':
    app.run()