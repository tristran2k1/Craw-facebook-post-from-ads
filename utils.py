import string
import dateparser
from datetime import datetime
import time
import re
import json
import requests

def parse_datetime(text: str):
    settings = {
        'RELATIVE_BASE': datetime.today().replace(minute=0, hour=0, second=0, microsecond=0)
    }

    result = dateparser.parse(text, settings=settings)
    if result:
        return result.replace(microsecond=0)
    return None

def strip_emoji(text):
    RE_EMOJI = re.compile(u'([\U00002600-\U000027BF])|([\U0001f300-\U0001f64F])|([\U0001f680-\U0001f6FF])')
    return RE_EMOJI.sub(r'', text)

def clean_text(text):
    result = strip_emoji(text)    
    result = result.replace('\n', '')
    result = result.replace(' ', '')
    return result

def remove_substring(content, removeText):
    edit_post_content_list = content.split(removeText)
    return ' '.join(edit_post_content_list)

# count how many element is existed in page
async def count_element_exist(page, element):
    list_element = page.locator(element)
    return await list_element.count()

class UrlToUidConverter:
    def __init__(self) -> None:
        self.__latest = datetime.now()
        self.delay_default = 4 # in minute

    def url_to_uid(self, url) -> string:
        self.__current = datetime.now()
        gap_time = self.__current - self.__latest
        self.__latest = self.__current

        if gap_time.seconds/60 >= self.delay_default: # in minute
            time.sleep(self.delay_default - gap_time.seconds/60)
            headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8",'accept': 'application/json, text/javascript, */*; q=0.01'}
            payload = {'link':url}
            with requests.Session() as session:
                res = session.post('https://id.traodoisub.com/api.php',headers=headers,data=payload)
                return json.loads(res.text)['id']
        
FACEBOOK_CONVERTER = UrlToUidConverter()