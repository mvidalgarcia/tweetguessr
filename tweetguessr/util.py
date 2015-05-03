import unicodedata
import re
from lib.facepp import API

API_KEY = '7e4592c4251cbfeff378bb585cc60c6e'
API_SECRET = 'DK1zSC6_vjhQL8ihl7b_h16mp-ZnEXHL'


def strip_accents(s):
    l_norm = []
    l = s.split('ñ')
    for item in l:
        l_norm.append(''.join(c for c in unicodedata.normalize('NFD', item)
                              if unicodedata.category(c) != 'Mn'))
    return 'ñ'.join(l_norm)


def strip_punctuation(s):
    return re.sub(r'[^\w]', ' ', s)


def gender_by_profile_image(url_image):
    """
    Image recognition using a third party library "Face++"
    :param url_image: Image url to analyse
    :return: dict of gender and confidence if there's just one face, None in other cases.
    """
    api = API(API_KEY, API_SECRET)
    face = api.detection.detect(url=url_image)
    res = None
    if len(face['face']) == 1:
        res = {'gender': face['face'][0]['attribute']['gender']['value'].lower(),
               'confidence': face['face'][0]['attribute']['gender']['confidence']}
    return res