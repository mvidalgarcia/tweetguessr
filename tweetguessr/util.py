import unicodedata
import re
import os
import math
from tweetguessr.lib.facepp import API

current_path = os.path.dirname(__file__)

API_KEY = '7e4592c4251cbfeff378bb585cc60c6e'
API_SECRET = 'DK1zSC6_vjhQL8ihl7b_h16mp-ZnEXHL'

STOPWORDS_PATH = current_path + '/data/stopwords.data'
FACEPP_CACHE_PATH = current_path + '/data/facepp_cache.tsv'


class Util:
    """
    Auxiliar functions
    """
    stopwords = set()
    facepp_cache = dict()

    def __init__(self, face_recognition=False):
        self.load_stopwords()
        if face_recognition:
            self.load_facepp_cache()

    def remove_accents(self, s):
        l_norm = []
        l = s.split('ñ')
        for item in l:
            l_norm.append(''.join(c for c in unicodedata.normalize('NFD', item)
                                  if unicodedata.category(c) != 'Mn'))
        return 'ñ'.join(l_norm)

    def remove_punctuation(self, s):
        return re.sub(r'[^\w]', ' ', s)

    def load_stopwords(self):
        with open(STOPWORDS_PATH) as file:
            for line in file:
                line_lst = line.split('|')
                stop_word = line_lst[0].strip()
                if stop_word:
                    self.stopwords.add(stop_word)

    def load_facepp_cache(self):
        """
        Load facepp image cache in a dictionary
        Dictionary format: url_profile_photo \t confidence (conf > 0 -> male, conf < 0 -> female)
        :return:
        """
        if not os.path.exists(FACEPP_CACHE_PATH):
            open(FACEPP_CACHE_PATH, 'w').close()
        with open(FACEPP_CACHE_PATH) as file:
            for line in file:
                line_lst = line.split('\t')
                if len(line_lst) == 2:
                    self.facepp_cache[line_lst[0]] = float(line_lst[1])

    def remove_stopwords(self, s):
        return ' '.join(word for word in s.split() if word not in self.stopwords)

    def remove_twitter_mentions(self, s):
        """
        Deletes twitter mentions e.g. 'Today @screen_name gives a speech' => 'Today gives a speech'
        :param s:
        :return:
        """
        s = re.sub(r'(?:[@])\S+', '', s)
        return " ".join(s.split())

    def remove_urls(self, s):
        """
        URLs Regular expression: http://daringfireball.net/2010/07/improved_regex_for_matching_urls
        :param s:
        :return:
        """
        s = re.sub(r'''(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', '', s, flags=re.MULTILINE)
        return ' '.join(s.split())

    def normalise(self, s, options=None):
        s = s.lower()
        if options is None:
            options = ['stopwords', 'accents', 'urls', 'twitter_mentions', 'punctuation']
            # options = []

        functions = {'accents': self.remove_accents, 'punctuation': self.remove_punctuation,
                     'urls': self.remove_urls, 'stopwords': self.remove_stopwords,
                     'twitter_mentions': self.remove_twitter_mentions}

        for opt in options:
            s = functions[opt](s)
        return s

    def gender_by_profile_image(self, url_image):
        """
        Image recognition using a third party library "Face++"
        :param url_image: Image url to analyse
        :return: dict of gender and confidence if there's just one face, None in other cases.
        """
        if url_image not in self.facepp_cache:
            res = None
            api = API(API_KEY, API_SECRET)
            try:
                face = api.detection.detect(url=url_image)
            except Exception:
                with open(FACEPP_CACHE_PATH, 'a+') as file:
                    line = '\t'.join([url_image, '0'])
                    file.write("%s\n" % line)
                return res

            if len(face['face']) == 1:
                # Save result when one face is found
                gender = face['face'][0]['attribute']['gender']['value'].lower()
                confidence = face['face'][0]['attribute']['gender']['confidence']
                res = {'gender': gender, 'confidence': confidence}
                with open(FACEPP_CACHE_PATH, 'a+') as file:
                    line = '\t'.join([url_image, str(confidence) if gender == 'male' else str(-confidence)])
                    file.write("%s\n" % line)

            else:
                with open(FACEPP_CACHE_PATH, 'a+') as file:
                    line = '\t'.join([url_image, '0'])
                    file.write("%s\n" % line)
        else:
            # Load gender and confidence from cache
            if self.facepp_cache[url_image] < 0:
                gender = 'female'
                confidence = abs(self.facepp_cache[url_image])
            else:
                gender = 'male'
                confidence = self.facepp_cache[url_image]
            res = {'gender': gender, 'confidence': confidence}

        return res

    def root_log_likelihood_ratio(self, a, b, c, d):
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
    util = Util()
    print(util.normalise('@juan Hola jesus@pepe.es que tal'.lower()))
    print(util.normalise("Jose Luis", ['accents', 'punctuation']))