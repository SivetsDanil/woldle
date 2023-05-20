from modes import Images

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
        json.dump(user_dict, open(f'users\\{user_dict["id"]}.json', 'w', encoding='utf8'), indent=4, ensure_ascii=False)
    response = {
        "response": {
            "end_session": end,
            "text": text,
            "tts": tts,
            "buttons": buttons + [{"title": "Меню", "hide": True}, {"title": "Настройки", "hide": True}, {"title": "Помощь", "hide": True}, {"title": "Что ты умеешь?", "hide": True}],
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
            user_dict = json.load(open(f'users\\{user}.json', encoding='utf8'))
            if user_dict["action"] == 'name':
                text = 'И снова здравствуй! Я так и не знаю твое имя:(\nСкажи, как тебя зовут?'
                return make_response(text=text, user_dict=user_dict)
            return menu(user_dict)
        except FileNotFoundError:
            user_dict = {"id": user, "name": "", "strike": 0, "old_words": [], "exp": 0, "color": "default",
                         "action": 'name', "word": "",
                         "Counter": 0, "language": "русском", "lange": 5, "level": "начинающий", "change_action": '',
                         "pages": 0, "цвет": "", "profile": "1533899/10f4f7f6494f62017c89"}
            text = f'{random.choice(helo)}! Давай знакомиться, я — Вордл, а тебя как зовут?'
            return make_response(text=text, user_dict=user_dict)
    user_dict = json.load(open(f'users\\{user}.json', encoding='utf8'))
    if user_request == 'хватит':
        return make_response(text='Возвращайся скорей!', user_dict=user_dict, end=True)
    if user_dict["action"] == "name":
        user_dict["name"] = user_request.capitalize()
        user_dict["action"] = "menu"
        return menu(user_dict)
    if user_request == "меню" or user_request == "выйти":
        return menu(user_dict)
    if user_request == 'настройки' or user_dict["action"] == "settings":
        if user_dict["name"] == '':
            user_dict["action"] = "name"
            return make_response(text=f'Пожалуйста, скажи свое имя, а то незнакомцам я с настройками не помогаю...',
                                 user_dict=user_dict)
        user_dict["action"] = 'changes'
        return settings(user_dict)
    if user_request == "помощь":
        return helper(user_dict)
    if user_request == "что ты умеешь":
        return what_I_can(user_dict)
    if user_dict["action"] == "changes":
        return changing(user_dict, user_request)
    if user_request == "персонализация" or user_dict["action"] == "pers":
        return personalization(user_dict)
    if user_dict["action"] == "pers_change":
        return pers_change(user_dict, user_request)
    if user_request == 'начать игру':
        return game(user_dict=user_dict)
    if user_request == "правила" or user_dict["action"] == "rules":
        return rules(user_request, user_dict)
    if user_request == "профиль" or user_dict["action"] == "profile":
        return profile(user_request, user_dict)
    if user_dict["action"] == 'game':
        return game(user_dict=user_dict, answer=user_request)
    if user_dict["action"] == "menu":
        return menu(user_dict)
    if user_dict["action"] == 'start_game':
        if yes_or_no(user_request) is None:
            return make_response(text=f'{random.choice(no_understand)}, что ты имеешь ввиду?', user_dict=user_dict)
        elif yes_or_no(user_request):
            user_dict["action"] = 'game'
            return game(user_dict)
        else:
            return make_response(text='Жаль, возвращайся ещё..', end=True, user_dict=user_dict)


def yes_or_no(answer):
    if answer in Yes_list:
        return True
    elif answer in No_list:
        return False
    else:
        return None


def rules(user_request, user_dict):
    user_request = user_request
    user_dict["action"] = "rules"
    buttons = [
        {
            "title": "Читать дальше",
            "hide": "false"
        }
    ]
    if user_request == "читать дальше":
        user_dict["pages"] += 1
    if user_request == "вернуться обратно":
        user_dict["pages"] -= 1
    rules = rules_pg1
    if user_dict["pages"] == 0:
        buttons = butt_1
        rules = rules_pg1
    if user_dict["pages"] == 1:
        buttons = butt_2
        rules = rules_pg2
    if user_dict["pages"] == 2:
        buttons = butt_2
        rules = rules_pg3
    if user_dict["pages"] == 3:
        buttons = butt_2
        rules = rules_pg4
    if user_dict["pages"] == 4:
        return make_response(text='Называя слова ты должен догадаться какое я ввел слово и назвать его.\nЕсли что-то забудешь, ты можешь сказать "Помощь".\nНу вот и все, веселись!', buttons=[{"title": "Вернуться обратно", "hide": False}, {"title": "Выйти", "hide": False}], user_dict=user_dict)
    return make_response(text="123", buttons=buttons, card=rules, user_dict=user_dict)


def helper(user_dict):
    return make_response(text=help_txt, user_dict=user_dict, buttons=[{"title": "Выйти", "hide": False}])


def what_I_can(user_dict):
    return make_response(text=commands_txt, user_dict=user_dict, buttons=[{"title": "Выйти", "hide": False}])


def profile(user_request, user_dict):
    user_dict["action"] = "profile"
    user_dict = user_dict
    card = {
        "type": "ItemsList",
        "header": {
            "text": "Профиль и статистика"
        },
        "items": [
            {
                "image_id": user_dict["profile"],
                "title": user_dict["name"],
                "description": "Ваше имя и аватар. Вы можете сменить своё имя в настройках, а аватар в персонализации!",
            },
            {
                "image_id": "1540737/64c216c73742a029cecb",
                "title": f"Отгадано слов: {len(user_dict['old_words'])}",
                "description": "Счётчик всех отгаданных слов по всем уровням сложности.",
            },
            {
                "image_id": "997614/cdd92f9bc9881157259f",
                "title": f"Опыт: {len(user_dict['old_words'])}",
                "description": "Показывает весь полученный опыт.\nЗа слова из сложности 'Начинающий' ты получаешь 1 уровень опыта.\nЗа 'Продвинутый' - 2 уровня. \nЗа 'Эксперт' - целых 3 уровня!",
            }
        ]
    }
    butt = [{"title": "Выйти", "hide": False}]
    return make_response(text="123", card=card, buttons=butt, user_dict=user_dict)


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
            return make_response(
                text=f'Я тебя не понял, пожалуйста, сказажи иначе...\nНа всякий случай, я даю слова от 3 до 6 букв',
                user_dict=user_dict)
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
            return make_response(text='Пожалуйста, выбери один из представленных или используй кнопки..',
                                 user_dict=user_dict)
        user_dict["action"] = 'settings'
        user_dict["level"] = user_request
        user_dict["change_action"] = ""
        return make_response(text=f'Теперь буду загадывать слова для уровня "{user_request.capitalize()}".',
                             user_dict=user_dict)
    elif user_request == 'смена языка':
        user_dict["action"] = 'settings'
        if user_dict["language"] == "русском":
            user_dict["language"] = 'английском'
            return make_response(text='Окей, сменил язык на английский', user_dict=user_dict)
        else:
            user_dict["language"] = 'русском'
            return make_response(text='Хорошо, поменял язык на русский', user_dict=user_dict)
    else:
        user_dict["action"] = 'settings'


def settings(user_dict):
    id = "1533899/e1884903b447c638793d" if user_dict["language"] == "русском" else "1533899/60d98b566a974e0dd613"
    settings = [
        {
            "image_id": "213044/65d24cd88052477d091e",
            "title": "Сменить твоё имя",
            "description": f"Сейчас: {user_dict['name']}.",
            "button": {"text": "Смена имени"}
        },
        {
            "image_id": "1030494/92020aab1af3f4a530b6",
            "title": "Изменить длину слов",
            "description": f"Сейчас: {user_dict['lange']}.",
            "button": {"text": "Смена длины"}
        },
        {
            "image_id": "997614/4b2eaba972fd1b62f060",
            "title": "Поменять сложность игры",
            "description": f"Сейчас твой уровень - {user_dict['level']}.",
            "button": {"text": "Смена сложности"}
        },
        {
            "image_id": id,
            "title": "Сменить язык слов",
            "description": f"Сейчас я загадываю на {user_dict['language']} языке.",
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
    user["action"] = "menu"
    user["pages"] = 0
    card = {
        "type": "ItemsList",
        "header": {
            "text": f'{random.choice(helo)}, {user["name"]}!'
        },
        "items": start_menu
    }
    return make_response(text=f'Привет, {user["name"]}!', card=card, user_dict=user)


def pers_change(user, request):
    user_dict = user
    user_request = request
    text = f'Выбирай:) Сейчас цвет твоего поля - {user_dict["цвет"]}'
    if user_request == "вперед":
        user_dict["pages"] = 1
        json.dump(user_dict, open(f'users\\{user_dict["id"]}.json', 'w', encoding='utf8'), indent=4, ensure_ascii=False)
    if user_request == "назад":
        user_dict["pages"] = 0
        json.dump(user_dict, open(f'users\\{user_dict["id"]}.json', 'w', encoding='utf8'), indent=4, ensure_ascii=False)
    pole_pg = pole_pg1 if user_dict["pages"] == 0 else pole_pg2
    butt = "Вперёд" if user_dict["pages"] == 0 else "Назад"
    if user_request == "апельсиновый":
        user_dict["color"] = "orange"
        user_dict["цвет"] = "апельсиновый"
        text = "Успешно! Теперь цвет твоего поля - апельсиновый"
    if user_request == "лазурный":
        user_dict["color"] = "azure"
        user_dict["цвет"] = "лазурный"
        text = "Успешно! Теперь цвет твоего поля - лазурный"
    if user_request == "морской":
        user_dict["color"] = "blue"
        user_dict["цвет"] = "морской"
        text = "Успешно! Теперь цвет твоего поля - морской"
    if user_request == "розовый фламинго":
        user_dict["color"] = "pink"
        user_dict["цвет"] = "розовый фламинго"
        text = "Успешно! Теперь цвет твоего поля - розовый фламинго"
    if user_request == "фиолетовая сирень":
        user_dict["color"] = "violet"
        user_dict["цвет"] = "фиолетовая сирень"
        text = "Успешно! Теперь цвет твоего поля - фиолетовая сирень"
    if user_request == "розовая агростемма":
        user_dict["color"] = "pink"
        user_dict["цвет"] = "розовая агростемма"
        text = "Успешно! Теперь цвет твоего поля - розовая агростемма"
    if user_request == "бирюзовый":
        user_dict["color"] = "light_blue"
        user_dict["цвет"] = "бирюзовый"
        text = "Успешно! Теперь цвет твоего поля - бирюзовый"
    if user_request == "красное яблоко":
        user_dict["color"] = "red"
        user_dict["цвет"] = "красное яблоко"
        text = "Успешно! Теперь цвет твоего поля - красное яблоко"
    if user_request == "пурпурный":
        user_dict["color"] = "purple"
        user_dict["цвет"] = "пурпурный"
        text = "Успешно! Теперь цвет твоего поля - пурпурный"
    if user_request == "классический":
        user_dict["цвет"] = "классический"
        user_dict["color"] = "default"
        text = "Успешно! Теперь цвет твоего поля - классический"
    if "Успешно" in text:
        return make_response(text=text, user_dict=user_dict)
    card = {
        "type": "ItemsList",
        "header": {
            "text": text
        },
        "items": pole_pg
    }
    buttons = [
        {
            "title": butt,
            "hide": "false"
        },
        {
            "title": "Меню",
            "hide": "true"
        }
    ]
    return make_response(text=f'', card=card, buttons=buttons, user_dict=user_dict)


def personalization(user_dict):
    user_dict["action"] = "pers_change"
    card = {
        "type": "ItemsList",
        "header": {
            "text": f'Персонализация!'
        },
        "items": personal
    }
    butt = [{"title": "Выйти", "hide": False}]
    return make_response(text=f'Персонализация', card=card, user_dict=user_dict, buttons=butt)


def game(user_dict, answer=''):
    Image = Images.Img(user_dict["lange"], user_dict["color"])
    user_dict["action"] = "game"
    words = rus_words[user_dict["lange"]]
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
                    "title": random.choice(start)
                }
            ]
        }
        return make_response(text="123", card=card, user_dict=user_dict)
    word = answer
    if len(word) != user_dict["lange"]:
        return make_response(text=f'Я жду от тебя слова длиной в {user_dict["lange"]} букв, можешь сменить режим в настройках.', user_dict=user_dict)
    elif word not in rus_play_words[user_dict["lange"]]:
        return make_response(text=f'Я не знаю такое слово, давай другое:(\nНапоминаю, мы используем только существительные', user_dict=user_dict)
    for i in range(user_dict["lange"]):
        if word[i] == user_dict["word"][i] or word[i] == '':
            Image.fill((0, 204, 0), i, user_dict["Counter"], word[i])
        elif word[i] in user_dict["word"]:
            Image.fill((244, 200, 0), i, user_dict["Counter"], word[i])
        Image.paster(word[i], i, user_dict["Counter"])
    image_id = yandex.downloadImageFile("Background.png")["id"]
    title = ""
    if user_dict['word'] == word:
        title = f'{random.choice(yes)}! Ты прав! Сыграем еще?'
        user_dict["old_words"].append(user_dict['word'])
        user_dict["action"] = 'start_game'
    elif user_dict["Counter"] == 6:
        title = f'{random.choice(fail)}, попытки кончились, это было слово "{user_dict["word"]}". Попробуешь еще?'
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
    return make_response(text="123", card=card, user_dict=user_dict)


if __name__ == '__main__':
    app.run(debug=True)
