import os
from util import *

current_path = os.path.dirname(__file__)


class GenderName:

    NAMES_PATH = current_path + '/data/names_INE.data'
    SURNAMES_PATH = current_path + '/data/surnames_INE.data'
    NAME_SURNAME_PATH = current_path + '/data/surnames_names_INE.data'

    names, name_surname = {}, {}
    surnames = []

    def __init__(self):
        self._load_data()

    def _load_data(self):
        self._load_names()
        self._load_surnames()
        self._load_name_surname()

    def _load_names(self):
        """
        :return: a dictionary whose items are this way: "Spanish name": <male_probability>
        Female prob can be easily calculated with (1 - male_probability)
        Source: Instituto Nacional de Estadística (INE)
        """
        with open(self.NAMES_PATH) as file:
            content = file.readlines()
        for line in content:
            line = line.rstrip().split('\t')
            self.names[line[0]] = line[2]

    def _load_surnames(self):
        """
        :return: a list of Spanish surnames
        Source: Instituto Nacional de Estadística (INE)
        """
        with open(self.SURNAMES_PATH) as file:
            self.surnames = [surname.rstrip() for surname in file.readlines()]

    def _load_name_surname(self):
        """
        :return: a dictionary whose items are this way:
        "Spanish name/surname": <probability_of_being_surname>
        Source: Instituto Nacional de Estadística (INE)
        """
        with open(self.NAME_SURNAME_PATH) as file:
            content = file.readlines()
        for line in content:
            line = line.rstrip().split('\t')
            self.name_surname[line[0]] = line[1]

    def fullname_gender(self, fullname):
        """
        :param fullname:
        :return: gender of the given fullname and confidence
        """
        # Lower case and strip accents
        fullname_stripped = strip_punctuation(strip_accents(fullname.lower()))
        fullname_list = fullname_stripped.split()
        result = {}
        result['fullname_given'] = fullname
        if len(fullname_list) <= 1:
            # if just one word (name, surname or whatever)
            result['gender'] = 'unknown'
            return result
        else:
            # determine full first name (normal or compound) and surnames
            firstname, surnames = [], []
            if not self._first_word_is_name(fullname_list[0], result, firstname):
                return result
            # iterate through the rest of words if we have a name
            for i in range(1, len(fullname_list)):
                item = fullname_list[i]
                if item in self.names:
                    if item in self.name_surname:
                        if float(self.name_surname[item]) <= 0.5:
                            firstname.append(item)
                            i += 1
                        else:
                            break
                    else:
                        firstname.append(item)
                        i += 1
                else:
                    break
            # names finished, continue with index i
            cache_surname = []  # for more-than-one-word surnames (i.e: de la rosa)
            for i in range(i, len(fullname_list)):
                item = fullname_list[i]
                # check if it's a valid surname
                if not cache_surname and self._add_valid_surname(item, result, surnames):
                    pass
                else:
                    cache_surname.append(item)
                    if self._add_valid_surname(' '.join(cache_surname), result, surnames):
                        cache_surname = []  # if more-than-one-word surname found, empty cache


            #surnames = [word for word in fullname_list if word not in firstname]
            result['firstname'] = firstname
            result['surnames'] = surnames
            #name_conf_male = self.names[fullname_list[0]] if fullname_list[0] in self.names else 'unknown'
            '''
            if name_conf_male == 'unknown':
                result['gender'] = 'unknown'
                return result
            elif float(name_conf_male) > 0.6:
                result['gender'] = 'male'
                result['confidence'] = name_conf_male
            elif 1 - float(name_conf_male) > 0.6:
                result['gender'] = 'female'
                result['confidence'] = 1 - float(name_conf_male)
                '''
            return result

    def _first_word_is_name(self, firstword, result, firstname):
        """
        :param firstword: first word of full name
        :param result: dict of results
        :return: True if it's a name, False if not
        """
        if firstword not in self.names:
            # check if first word is a name, if not save 'unknown'
            result['gender'] = 'unknown'
            return False
        else:
            firstname.append(firstword)
            return True

    def _add_valid_surname(self, word, result, surnames):
        """
        check if word is a valid surname
        :param word: word analysed
        :param result: dict of results
        :return: True if it's valid surname, False if not
        """
        if len(list(filter(lambda x: word == x, self.surnames))) > 0:
            surnames.append(word)
            return True
        else:
            result['gender'] = 'unknown'
            return False
