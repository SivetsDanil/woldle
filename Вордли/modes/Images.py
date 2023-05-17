import json
import requests
from PIL import Image, ImageDraw


class Img:
    def __init__(self, len, color):
        size_x = [104, 77, 61, 50]
        self.pos = size_x[len - 3]
        self.back = Image.open(f"fonts/{len}/{color}.png")

    def fill(self, color, x, y, letter):
        back = Image.open("Background.png")
        back = back.convert("RGB")
        lett = Image.open("letters/" + letter + ".png")
        param_x = ((self.pos - lett.size[0]) // 2) + 4 + (self.pos * x) + (6 * x)
        param_y = ((70 - lett.size[1]) // 2 + 4) + 4 + (70 * y) + (6 * y)
        seed = (param_x, param_y)
        ImageDraw.floodfill(back, seed, color, thresh=50)
        back.save("Background.png")

    def paster(self, letter, x, y):
        lett = Image.open("letters/" + letter+".png")
        back = Image.open("Background.png")
        param_x = ((self.pos - lett.size[0]) // 2) + 3 + (self.pos * x) + (4 * x)
        param_y = ((75 - lett.size[1]) // 2 + 4) + 3 + (75 * y) + (4 * y)
        if letter == "й":
            param_y -= 4
        back.paste(lett, (param_x, param_y), mask=lett)
        back.save("Background.png")

    def show(self):
        back = Image.open("Background.png")
        back.show()


    def clear(self):
        self.back.save("Background.png")


class YandexImages(object):
    def __init__(self):
        self.SESSION = requests.Session()

        self.API_VERSION = 'v1'
        self.API_BASE_URL = 'https://dialogs.yandex.net/api'
        self.API_URL = self.API_BASE_URL + '/' + self.API_VERSION + '/'
        self.skills = ''

    def set_auth_token(self, token):
        self.SESSION.headers.update(self.get_auth_header(token))

    def get_auth_header(self, token):
        return {
            'Authorization': 'OAuth %s' % token
        }

    def log(self, error_text, response):
        log_file = open('YandexApi.log', 'a')
        log_file.write(error_text + '\n')  # +response)
        log_file.close()

    def validate_api_response(self, response, required_key_name=None):
        content_type = response.headers['Content-Type']
        content = json.loads(response.text) if 'application/json' in content_type else None

        if response.status_code == 200:
            if required_key_name and required_key_name not in content:
                self.log('Unexpected API response. Missing required key: %s' % required_key_name, response=response)
                return None
        elif content and 'error_message' in content:
            self.log('Error API response. Error message: %s' % content['error_message'], response=response)
            return None
        elif content and 'message' in content:
            self.log('Error API response. Error message: %s' % content['message'], response=response)
            return None
        else:
            response.raise_for_status()

        return content

    def checkOutPlace(self):
        result = self.SESSION.get(self.API_URL + 'status')
        content = self.validate_api_response(result)
        if content != None:
            return content['images']['quota']
        return None


    def downloadImageUrl(self, url):
        path = 'skills/{skills_id}/images'.format(skills_id=self.skills)
        result = self.SESSION.post(url=self.API_URL + path, data=json.dumps({"url": url}))
        content = self.validate_api_response(result)
        if content != None:
            return content['image']
        return None


    def downloadImageFile(self, img):
        path = 'skills/{skills_id}/images'.format(skills_id=self.skills)
        result = self.SESSION.post(url=self.API_URL + path, files={'file': (img, open(img, 'rb'))})
        content = self.validate_api_response(result)
        if content != None:
            return content['image']
        return None


    def getLoadedImages(self):
        path = 'skills/{skills_id}/images'.format(skills_id=self.skills)
        result = self.SESSION.get(url=self.API_URL + path)
        content = self.validate_api_response(result)
        if content != None:
            return content['images']
        return None

    def deleteImage(self, img_id):
        path = 'skills/{skills_id}/images/{img_id}'.format(skills_id=self.skills, img_id=img_id)
        result = self.SESSION.delete(url=self.API_URL + path)
        content = self.validate_api_response(result)
        if content != None:
            return content['result']
        return None

    def deleteAllImage(self):
        success = 0
        fail = 0
        images = self.getLoadedImages()
        for image in images:
            image_id = image['id']
            if image_id:
                if self.deleteImage(image_id):
                    success += 1
                else:
                    fail += 1
            else:
                fail += 1

        return {'success': success, 'fail': fail}




