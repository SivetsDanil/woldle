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


def make_response(text=None, card=None, tts=None, buttons=[], end=False, user={}):
    json.dump(user, open(f'{user["id"]}.json', 'w', encoding='utf8'), indent=4, ensure_ascii=False)
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
    try:
        user_dict = json.load(open(f'{user}.json', encoding='utf8'))
    except:
        pass
    if event["session"]["new"]:
        try:
            user_dict = json.load(open(f'{user}.json', encoding='utf8'))
        except:
            user_dict = {"id": user, "name": "", "strike": 0, "old_words": [], "action": 'name', "word": "",
                         "Counter": 0, "language": "rus", "lange": 5, "level": "beginner", "change_action": ''}
            text = 'Привет! Давай знакомиться, меня зовут Вордл, а тебя?'
            return make_response(text=text, user=user_dict)
        if json.load(open(f'{user}.json', encoding='utf8'))["action"] == 'name':
            text = 'И снова здравствуй! Я так и не знаю твое имя:(\nСкажи, как тебя зовут?'
            return make_response(text=text, user=user_dict)
        else:
            user_dict = json.load(open(f'{user}.json', encoding='utf8'))
            user_dict["action"] = 'rules'
            return make_response(text=f'Привет, {user_dict["name"]}! Помнишь правила игры?', user=user_dict)
    if user_dict["action"] == "changes":
        if user_request == 'выйти':
            user_dict["action"] = 'start_game'
            return make_response(text='Надеюсь я тебе помог)\nНачинаем игру?', user=user_dict)
        elif user_request == 'смена имени':
            user_dict["change_action"] = 'change_name'
            return make_response(text='Скажи мне, как тебя теперь называть?', user=user_dict)
        elif user_dict["change_action"] == 'change_name':
            user_dict["action"] = 'settings'
            user_dict["name"] = user_request.capitalize()
            user_dict["change_action"] = ""
            return make_response(text=f'Теперь буду звать тебя {user_request.capitalize()};)', user=user_dict)
        elif user_request == 'смена длины':
            user_dict["change_action"] = 'change_lange'
            return make_response(text='Скажи, какой длины от 3 до 6 букв давать слова?', user=user_dict)
        elif user_dict["change_action"] == 'change_lange':
            user_dict["action"] = 'settings'
            if "три" in user_request:
                user_dict["lange"] = 3
            elif "чет" in user_request:
                user_dict["lange"] = 4
            elif "пят" in user_request:
                user_dict["lange"] = 5
            elif "шест" in user_request:
                user_dict["lange"] = 6
            else:
                return make_response(text=f'Я тебя не понял, пожалуйста, сказажи иначе...', user=user_dict)
            user_dict["change_action"] = ""
            return make_response(text=f'Теперь буду загадывать слова по {user_request} букв.', user=user_dict)
        elif user_request == 'смена сложности':
            user_dict["change_action"] = 'change_level'
            return make_response(text='Скажи мне, какой сложности загадывать слова?\nВыбор из: "Начинающий", "Игрок wordle" и "Эрудита"', user=user_dict)
        elif user_dict["change_action"] == 'change_level':
            user_dict["action"] = 'settings'
            user_dict["level"] = user_request
            user_dict["change_action"] = ""
            return make_response(text=f'Теперь буду загадывать слова для уровня {user_request}.', user=user_dict)
        elif user_request == 'смена языка':
            user_dict["change_action"] = 'change_language'
            return make_response(text='Какой язык выберешь: русский или английский?', user=user_dict)
        elif user_dict["change_action"] == 'change_language':
            user_dict["action"] = 'settings'
            user_dict["language"] = user_request
            user_dict["change_action"] = ""
            return make_response(text=f'Теперь буду загадывать слова из языка {user_request}.', user=user_dict)
        else:
            user_dict["action"] = 'settings'
    if user_request == 'настройки' or user_dict["action"] == "settings":
        if user_dict["name"] == '':
            return make_response(text=f'Скажи свое имя, незнакомцам с настройками не помогаю...', user=user_dict)
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
        user_dict["action"] = 'changes'
        card = {
            "type": "ItemsList",
            "header": {
                "text": "Итак, ты в настройках."
            },
            "items": settings,
        }
        text = "Ты в настройках, выбери что хочешь изменить."
        buttons = [{"title": "Выйти", "hide": False}]
        return make_response(text=text, card=card, user=user_dict, buttons=buttons)
    else:
        if user_dict["action"] == 'name':
            user_dict['name'] = user_request.capitalize()
            text = f"Приятно познакомиться, {user_dict['name']}! Знаешь правила игры wordle?"
            user_dict["action"] = 'rules'
            return make_response(text=text, user=user_dict)
        elif user_dict["action"] == 'rules':
            if yes_or_no(user_request) is None:
                return make_response(text='Не понял тебя, что ты имеешь ввиду?', user=user_dict)
            elif yes_or_no(user_request):
                user_dict["action"] = 'start_game'
                return make_response(text="Отлично! Стартуем игру?", user=user_dict)
            else:
                user_dict["action"] = 'start_game'
                return make_response(text=rules + "\nНачинаем играть?", user=user_dict)
        elif user_dict["action"] == 'start_game':
            if yes_or_no(user_request) is None:
                return make_response(text='Не понял тебя, что ты имеешь ввиду?', user=user_dict)
            elif yes_or_no(user_request):
                user_dict["action"] = 'game'
                return game(user_dict)
            else:
                return make_response(text='Жаль, возвращайся ещё..', end=True, user=user_dict)
        elif user_dict["action"] == 'game':
            return game(user_dict, user_request)


def yes_or_no(answer):
    if answer in Yes_list:
        return True
    elif answer in No_list:
        return False
    else:
        return None


def game(user_dict, answer='', mode=5, words=rus_words_5):
    if user_dict['word'] == '' or answer == '':
        user_dict['word'] = random.choice(list(set(words) - set(user_dict["old_words"]))).strip()
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
        return make_response(text="123", card=card, user=user_dict)
    word = answer
    if len(word) != 5:
        return make_response(text=f'Я жду от тебя слова длиной в {mode} букв, можешь сменить режим в настройках.', user=user_dict)
    elif word not in words:
        return make_response(text=f'Я не знаю такое слово, давай другое:(\nНапоминаю, мы используем только существительные', user=user_dict)
    for i in range(mode):
        if word[i] == user_dict["word"][i] or word[i] == '':
            Image.fill((0, 204, 0), i, user_dict["Counter"])
        elif word[i] in user_dict["word"]:
            Image.fill((244, 200, 0), i, user_dict["Counter"])
        Image.paster(word[i], i, user_dict["Counter"])
    image_id = yandex.downloadImageFile("Background.png")["id"]
    title = ''
    if user_dict['word'] == word:
        title = 'Отлично, ты прав! Сыграем еще?'
        user_dict["old_words"].append(user_dict['word'])
        user_dict["action"] = 'start_game'
    elif user_dict["Counter"] == 4:
        title = f'Попытки кончились, это было слово "{user_dict["word"]}". Попробуешь еще?'
        user_dict["action"] = 'start_game'
    card = {
        "type": "ImageGallery",
        "items": [
            {
                "image_id": image_id,
                "title": title
            }
        ]
    }
    user_dict["Counter"] += 1
    return make_response(text="123", card=card, user=user_dict)


if __name__ == '__main__':
    app.run()