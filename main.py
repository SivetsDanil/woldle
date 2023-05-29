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
    try:
        response = handler(request.json, response)
    except Exception as e:
        return json.dumps(make_response(text='Непредвиденная ошибка: ' + str(e)))
    logging.info(f"Response: {response!r}")
    return json.dumps(response)


def make_response(text="null", card=None, tts=None, buttons=[], end=False, user_dict={}):
    if user_dict != {}:
        json.dump(user_dict, open(f'mysite/users/{user_dict["id"]}.json', 'w', encoding='utf8'), indent=4,
                  ensure_ascii=False)
    response = {
        "response": {
            "end_session": end,
            "text": text,
            "tts": tts,
            "buttons": buttons + [{"title": "Меню", "hide": True}, {"title": "Настройки", "hide": True},
                                  {"title": "Помощь", "hide": True}, {"title": "Что ты умеешь?", "hide": True}],
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
            user_dict = json.load(open(f'mysite/users/{user}.json', encoding='utf8'))
            if user_dict["action"] == 'name':
                text = 'И снова здравствуй! Я так и не знаю твое имя:(\nСкажи, как тебя зовут?'
                return make_response(text=text, user_dict=user_dict)
            return menu(user_dict)
        except FileNotFoundError:
            user_dict = {"id": user, "name": "", "strike": 0, "old_words": [], "exp": 0, "color": "default",
                         "action": 'name', "word": "",
                         "Counter": 0, "language": "русском", "lange": 5, "level": "начинающий", "change_action": '',
                         "pages": 0, "цвет": "", "profile": "1533899/10f4f7f6494f62017c89", "about_user": ''}
            text = f'{random.choice(helo)}! Я — Вордл, а тебя как называть?'
            file1 = open("mysite/users/1_users_top.json")
            top_file = json.load(file1)
            top_file[user_dict["id"]] = [user_dict["exp"], user_dict["id"]]
            file2 = open("mysite/users/1_users_top.json", 'w', encoding='utf8')
            json.dump(top_file, file2, indent=4, ensure_ascii=False)
            file1.close()
            file2.close()
            return make_response(text=text, user_dict=user_dict)
    user_dict = json.load(open(f'mysite/users/{user}.json', encoding='utf8'))
    if len(user_dict) != 17:
        user_example = {"id": user, "name": "", "strike": 0, "old_words": [], "exp": 0, "color": "default",
                        "action": 'name', "word": "",
                        "Counter": 0, "language": "русском", "lange": 5, "level": "начинающий", "change_action": '',
                        "pages": 0, "цвет": "", "profile": "1533899/10f4f7f6494f62017c89", "about_user": ''}
        for r in user_example:
            if r not in user_dict:
                user_dict[r] = user_example[r]
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
            return make_response(text='Пожалуйста, скажи свое имя, а то незнакомцам я с настройками не помогаю...',
                                 user_dict=user_dict)
        user_dict["action"] = 'changes'
        return settings(user_dict)
    if user_request == "помощь":
        return helper(user_dict)
    if user_request == "что ты умеешь":
        return what_I_can(user_dict)
    if user_dict["action"] == "changes":
        return changing(user_dict, user_request)
    if user_request == "поле" or user_dict["action"] == "pers_change":
        return pers_change(user_dict, user_request)
    if user_request == "аватарка" or user_dict["action"] == "pers_profile":
        return pers_profile(user_request, user_dict)
    if user_request == "о себе" or user_dict["action"] == "info":
        return pers_info(user_dict, user_request)
    if user_request == "персонализация" or user_dict["action"] == "pers":
        return personalization(user_dict)
    if user_dict["action"] == "pers_change":
        return pers_change(user_dict, user_request)
    if user_request == 'начать игру':
        return game(user_dict=user_dict)
    if user_request == "правила" or user_dict["action"] == "rules":
        return rules(user_request, user_dict)
    if user_request == "топ игроков" or user_dict["action"] == "top":
        if user_dict["action"] == "top":
            return top(user_dict, user_request)
        return top(user_dict)
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
        return make_response(
            text='Называя слова ты должен догадаться какое я ввел слово и назвать его.\nЕсли что-то забудешь, ты можешь сказать "Помощь".\nНу вот и все, веселись!',
            buttons=[{"title": "Вернуться обратно", "hide": False}, {"title": "Выйти", "hide": False}],
            user_dict=user_dict)
    return make_response(text="Внимательно изучи  нформацию на карточках", buttons=buttons, card=rules,
                         user_dict=user_dict)


def helper(user_dict):
    return make_response(text=help_txt, user_dict=user_dict, buttons=[{"title": "Выйти", "hide": False}])


def what_I_can(user_dict):
    return make_response(text=commands_txt, user_dict=user_dict, buttons=[{"title": "Выйти", "hide": False}])


def profile(user_request, user_dict):
    user_dict["action"] = "profile"
    user_dict = user_dict
    if user_request == "заметки":
        if user_dict["about_user"] == "":
            return make_response(text="Вы пока не оставили ни одной заметки о себе! Написать эти заметки можно в разделе 'Персонализация'")
        return make_response(text=user_dict["about_user"])
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
                "image_id": "213044/a285810dc8dd1b0358ce",
                "title": "О себе",
                "description": "Нажмите, чтобы посмотреть заметки о себе. Эти заметки уидят другие игроки, если вы попадёте в топ! Изменить их можно в персонализации.",
                "button": {"text": "Заметки"}
            },
            {
                "image_id": "1540737/64c216c73742a029cecb",
                "title": f"Отгадано слов: {len(user_dict['old_words'])}",
                "description": "Счётчик всех отгаданных слов по всем уровням сложности.",
            },
            {
                "image_id": "997614/cdd92f9bc9881157259f",
                "title": f"Опыт: {user_dict['exp']}",
                "description": "Показывает весь полученный опыт.\nЗа слова из сложности 'Начинающий' ты получаешь 1 уровень опыта.\nЗа 'Продвинутый' - 2 уровня. \nЗа 'Эксперт' - целых 3 уровня!",
            },
            {
                "image_id": "1533899/6e6e74866a5a41c9146a",
                "title": "Топ наших игроков!",
                "description": f"Тут ты можешь посмотреть профили лучших",
                "button": {"text": "Топ игроков"}
            }
        ]
    }
    butt = [{"title": "Выйти", "hide": False}]
    return make_response(text="Ты во вкладке профиль и статистика, что дальше?", card=card, buttons=butt,
                         user_dict=user_dict)


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
                text='Я тебя не понял, пожалуйста, сказажи иначе...\nНа всякий случай, я даю слова от 3 до 6 букв',
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
    user["change_action"] = ""
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


def pers_profile(user_request, user_dict):
    user_dict["action"] = "pers_profile"
    user_dict = user_dict
    user_request = user_request
    profile_pg = profile_pg1
    buttons = butt1
    if user_request == "вперед":
        user_dict["pages"] += 1
    if user_request == "назад":
        user_dict["pages"] -= 1
    if user_dict["pages"] == 0:
        buttons = butt1
    if user_dict["pages"] == 1:
        profile_pg = profile_pg2
        buttons = butt2
    if user_dict["pages"] == 2:
        profile_pg = profile_pg3
        buttons = butt2
    if user_dict["pages"] == 3:
        profile_pg = profile_pg4
        buttons = butt2
    if user_dict["pages"] == 4:
        profile_pg = profile_pg5
        buttons = butt3
    if user_request == "аватарка 1":
        user_dict["profile"] = "997614/d5f89372f09dd947d281"
    if user_request == "аватарка 2":
        user_dict["profile"] = "997614/cc561fc174761f3eca0f"
    if user_request == "аватарка 3":
        user_dict["profile"] = "213044/ea248348522f123dc0fb"
    if user_request == "аватарка 4":
        user_dict["profile"] = "1656841/250cf05db6a5750a6c5e"
    if user_request == "аватарка 5":
        user_dict["profile"] = "213044/084a4e19e1e968c1a306"
    if user_request == "аватарка 6":
        user_dict["profile"] = "997614/c173e1dd62892307f0ae"
    if user_request == "аватарка 7":
        user_dict["profile"] = "213044/30df3ffcb27989c51e62"
    if user_request == "аватарка 8":
        user_dict["profile"] = "1521359/d94bd2f9f79ff54a24f1"
    if user_request == "аватарка 9":
        user_dict["profile"] = "997614/ddc2be1287b1588c8485"
    if user_request == "аватарка 10":
        user_dict["profile"] = "1652229/b2c6e1e96d01c44a7ed4"
    if user_request == "аватарка 11":
        user_dict["profile"] = "213044/f93e33cf04dcd2533a72"
    if user_request == "аватарка 12":
        user_dict["profile"] = "1533899/3238236bdd35275373d1"
    if user_request == "аватарка 13":
        user_dict["profile"] = "1540737/ddaba0f752b31a57e51f"
    if user_request == "аватарка 14":
        user_dict["profile"] = "1652229/7f1a2a309c2f97ea6dac"
    if user_request == "аватарка 15":
        user_dict["profile"] = "1540737/227fb70203df0e937a4c"
    if user_request == "аватарка 16":
        user_dict["profile"] = "1540737/095fcc5f992ba9aafc59"
    if user_request == "аватарка 17":
        user_dict["profile"] = "1540737/227fb70203df0e937a4c"
    if user_request == "аватарка 18":
        user_dict["profile"] = "997614/a68df4fd9e6770f0348c"
    if user_request == "аватарка 19":
        user_dict["profile"] = "1652229/5e392a889dee16f10045"
    if user_request == "аватарка 20":
        user_dict["profile"] = "1652229/1dfbd6a18b6df501a9f1"
    if user_request == "аватарка 21":
        user_dict["profile"] = "1540737/95686d8980d3074a82e0"
    if user_request == "аватарка 22":
        user_dict["profile"] = "997614/51782e9580c419cc6f3f"
    if user_request == "аватарка 23":
        user_dict["profile"] = "1521359/5ee13710f746b8837655"
    if user_request == "аватарка 24":
        user_dict["profile"] = "937455/5c0b5a9ef5efeb54ec1a"
    if user_request == "аватарка 25":
        user_dict["profile"] = "1533899/1e45fc5023b5056ecd5e"
    if "аватарка " in user_request:
        return make_response(text='Успешно!', user_dict=user_dict)
    card = {
        "type": "ItemsList",
        "header": {
            "text": 'Тут ты можешь выбрать аватарку, которая тебе больше всего нравится!'
        },
        "items": profile_pg
    }
    return make_response(text='Выбирай любую аватарку! Обрати внимание, тут две вкладки.', card=card, buttons=buttons,
                         user_dict=user_dict)


def pers_info(user_dict, user_request):
    user_dict["action"] = "info"
    if user_request == "о себе":
        text = "Записываю..."
    else:
        user_dict["about_user"] = user_request
        text = "Успешно!"
    return make_response(text=text, user_dict=user_dict)


def pers_change(user, request):
    user_dict = user
    user_request = request
    user_dict["action"] = "pers_change"
    text = f'Выбирай:) Сейчас цвет твоего поля - {user_dict["цвет"]}'
    if user_request == "вперед":
        user_dict["pages"] = 1
    if user_request == "назад":
        user_dict["pages"] = 0
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
        }
    ]
    return make_response(text='Выбирай любое оформление!', card=card, buttons=buttons, user_dict=user_dict)


def personalization(user_dict):
    user_dict["action"] = "pers"
    card = {
        "type": "ItemsList",
        "header": {
            "text": 'Персонализация!'
        },
        "items": personal
    }
    butt = [{"title": "Выйти", "hide": False}]
    return make_response(text='Что ты хочешь изменить?', card=card, user_dict=user_dict, buttons=butt)


def game(user_dict, answer=''):
    Image = Images.Img(user_dict["lange"], user_dict["color"])
    user_dict["action"] = "game"
    if user_dict["language"] == "русском":
        words = rus_words[user_dict["lange"]][user_dict["level"]]
        play_words = rus_play_words
    else:
        words = eng_words[user_dict["lange"]][user_dict["level"]]
        play_words = eng_play_words
    if user_dict['word'] == '' or answer == '':
        user_dict['word'] = random.choice(list(set(words) - set(user_dict["old_words"]))).strip()
        user_dict['word'].replace('ё', "е")
        Image.clear(user_dict["id"])
        user_dict["Counter"] = 0
        image_id = yandex.downloadImageFile(f"mysite/users_fonts/{user_dict['id']}.png")["id"]
        card = {
            "type": "ImageGallery",
            "items": [
                {
                    "image_id": image_id,
                    "title": random.choice(start)
                }
            ]
        }
        return make_response(text=random.choice(start), card=card, user_dict=user_dict)
    word = answer
    if len(word) != user_dict["lange"]:
        return make_response(
            text=f'Я жду от тебя слова длиной в {user_dict["lange"]} букв, можешь сменить режим в настройках.',
            user_dict=user_dict)
    elif word not in play_words[user_dict["lange"]]:
        return make_response(
            text=f'Я не знаю такое слово, давай другое:(\nНапоминаю, мы используем только существительные',
            user_dict=user_dict)
    for i in range(user_dict["lange"]):
        if word[i] == user_dict["word"][i] or word[i] == '':
            Image.fill(user_dict["id"], (0, 204, 0), i, user_dict["Counter"], word[i])
        elif word[i] in user_dict["word"]:
            Image.fill(user_dict["id"], (244, 200, 0), i, user_dict["Counter"], word[i])
        Image.paster(user_dict["id"], word[i], i, user_dict["Counter"])
    image_id = yandex.downloadImageFile(f'mysite/users_fonts/{user_dict["id"]}.png')["id"]
    title = ""
    if user_dict['word'] == word:
        title = f'{random.choice(yes)}! Ты прав! Сыграем еще?'
        if user_dict["level"] == "начинающий":
            user_dict["exp"] += 1
        if user_dict["level"] == "продвинутый":
            user_dict["exp"] += 2
        if user_dict["level"] == "эрудит":
            user_dict["exp"] += 3
        file1 = open("mysite/users/1_users_top.json")
        top_file = json.load(file1)
        top_file[user_dict["id"]] = [user_dict["exp"], user_dict["id"]]
        file2 = open("mysite/users/1_users_top.json", 'w', encoding='utf8')
        json.dump(top_file, file2, indent=4, ensure_ascii=False)
        file1.close()
        file2.close()
        user_dict["old_words"].append(user_dict['word'])
        user_dict["action"] = 'start_game'
    elif user_dict["Counter"] == 5:
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
    return make_response(text=title, card=card, user_dict=user_dict)


def top(user_dict, user_request=''):
    top_file = json.load(open("mysite/users/1_users_top.json", encoding='utf8')).values()
    users_top = []
    sorted_top = sorted(top_file, key=lambda x: x[0], reverse=True)
    for r in sorted_top[:5]:
        users_top.append(r[1])
    user_1 = json.load(open(f'mysite/users/{users_top[0]}.json', encoding='utf8'))
    user_2 = json.load(open(f'mysite/users/{users_top[1]}.json', encoding='utf8'))
    user_3 = json.load(open(f'mysite/users/{users_top[2]}.json', encoding='utf8'))
    user_4 = json.load(open(f'mysite/users/{users_top[3]}.json', encoding='utf8'))
    user_5 = json.load(open(f'mysite/users/{users_top[4]}.json', encoding='utf8'))
    if user_request == '':
        top = [
            {
                "image_id": f"{user_1['profile']}",
                "title": "Топ 1 игрок навыка - самый крутой",
                "description": f"{user_1['name']} - {user_1['exp']} очков",
                "button": {"text": f"{user_1['name']}"}
            },
            {
                "image_id": f"{user_2['profile']}",
                "title": "Почетное второе место!",
                "description": f"{user_2['name']} - {user_2['exp']} очков",
                "button": {"text": f"{user_2['name']}"}
            },
            {
                "image_id": f"{user_3['profile']}",
                "title": "Бронза! Попал в топ 3.",
                "description": f"{user_3['name']} - {user_3['exp']} очков",
                "button": {"text": f"{user_3['name']}"}
            },
            {
                "image_id": f"{user_4['profile']}",
                "title": "4 место среди всех игроков",
                "description": f"{user_4['name']} - {user_4['exp']} очков",
                "button": {"text": f"{user_4['name']}"}
            },
            {
                "image_id": f"{user_5['profile']}",
                "title": "Заключающее звено топа!",
                "description": f"{user_5['name']} - {user_5['exp']} очков",
                "button": {"text": f"{user_5['name']}"}
            }
        ]
        card = {
            "type": "ItemsList",
            "header": {
                "text": f"Вот наш топ игроков! Ты на {sorted_top.index([user_dict['exp'], user_dict['id']]) + 1} месте!"
            },
            "items": top,
        }
        user_dict["action"] = "top"
        return make_response(text="Вот наш топ игроков", card=card, user_dict=user_dict, buttons=[{"title": "Выйти", "hide": False}])
    else:
        user = list(filter(lambda x: x['name'] == user_request.capitalize(), [user_5, user_4, user_3, user_2, user_1]))[0]
        card = {
            "type": "ItemsList",
            "header": {
                "text": f"Профиль игрока {user['name']}"
            },
            "items": [
                {
                    "image_id": user["profile"],
                    "title": user["name"],
                    "description": "Имя и аватар игрока.",
                },
                {
                    "image_id": "1540737/64c216c73742a029cecb",
                    "title": f"Отгадано слов: {len(user['old_words'])}",
                    "description": "Счётчик всех отгаданных слов по всем уровням сложности.",
                },
                {
                    "image_id": "997614/cdd92f9bc9881157259f",
                    "title": f"Опыт: {user['exp']}",
                    "description": "Опыт, благодаря которому можно попасть в топ",
                },
                {
                    "image_id": '213044/a285810dc8dd1b0358ce',
                    "title": "Записи о себе",
                    "description": f"{user['about_user']}",
                }
            ]
        }
        return make_response(text=f"Профиль игрока {user['name']}", card=card, user_dict=user_dict, buttons=[{"title": "Выйти", "hide": False}])


if __name__ == '__main__':
    app.run(debug=True)
