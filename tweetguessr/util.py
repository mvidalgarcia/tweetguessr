import unicodedata
import re
import os
import math
from lib.facepp import API

current_path = os.path.dirname(__file__)

API_KEY = '7e4592c4251cbfeff378bb585cc60c6e'
API_SECRET = 'DK1zSC6_vjhQL8ihl7b_h16mp-ZnEXHL'

STOPWORDS_PATH = current_path + '/data/stopwords.data'


def remove_accents(s):
    l_norm = []
    l = s.split('ñ')
    for item in l:
        l_norm.append(''.join(c for c in unicodedata.normalize('NFD', item)
                              if unicodedata.category(c) != 'Mn'))
    return 'ñ'.join(l_norm)


def remove_punctuation(s):
    return re.sub(r'[^\w]', ' ', s)


def load_stopwords():
    stopwords = set()
    with open(STOPWORDS_PATH) as file:
        for line in file:
            line_lst = line.split('|')
            if line_lst:
                stopword = line_lst[0].strip()
                if stopword:
                    stopwords.add(stopword)
    return stopwords


def remove_stopwords(s):
    stopwords = load_stopwords()
    for stopword in stopwords:
        s = re.sub(r"\b%s\b" % stopword, '', s)
    return " ".join(s.split())


def remove_twitter_mentions(s):
    """
    Deletes twitter mentions e.g. 'Today @screen_name gives a speech' => 'Today gives a speech'
    :param s:
    :return:
    """
    s = re.sub(r'(?:[@])\S+', '', s)
    return " ".join(s.split())


def remove_urls(s):
    """
    URLs Regular expression: http://daringfireball.net/2010/07/improved_regex_for_matching_urls
    :param s:
    :return:
    """
    s = re.sub(r'''(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', '', s, flags=re.MULTILINE)
    return " ".join(s.split())


def normalise(s, options=None):
    if options is None:
        s = s.lower()
        options = ['accents', 'urls', 'twitter_mentions', 'punctuation', 'stopwords']

    functions = {'accents': remove_accents, 'punctuation': remove_punctuation,
                 'urls': remove_urls, 'stopwords': remove_stopwords,
                 'twitter_mentions': remove_twitter_mentions}

    for opt in options:
        s = functions[opt](s)

    return s


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


def root_log_likelihood_ratio(a, b, c, d):
    """
    This implementation is based on LLR interpretation provided in the following
    paper (see table and equations in page 7): *
    Java, Akshay, et al. "Why we twitter: understanding microblogging usage and
    communities." Proceedings of the 9th WebKDD and 1st SNA-KDD 2007 workshop on
    Web mining and social network analysis. ACM, 2007.
    Available at: http://aisl.umbc.edu/resources/369.pdf *
    :param a: frequency of token of interest in dataset A
    :param b: frequency of token of interest in dataset B
    :param c: total number of observations in dataset A
    :param d: total number of observations in dataset B
    :return: LLR value
    """
    e1 = c * (a + b) / (c + d)
    e2 = d * (a + b) / (c + d)
    # To avoid a division by 0 if a or b equal 0 they are replaced by 1
    result = 2 * (a * math.log(a / e1 + (1 if a == 0 else 0)) + b * math.log(b / e2 + (1 if b == 0 else 0)))
    result = math.sqrt(result)
    if a / c < b / d:
        result = -result
    return result

if __name__ == "__main__":
    print(normalise('@juan Hola jesus@pepe.es que tal'))