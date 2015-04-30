import unicodedata
import re


def strip_accents(s):
    l_norm = []
    l = s.split('ñ')
    for item in l:
        l_norm.append(''.join(c for c in unicodedata.normalize('NFD', item)
                              if unicodedata.category(c) != 'Mn'))
    return 'ñ'.join(l_norm)


def strip_punctuation(s):
    return re.sub(r'[^\w]', ' ', s)