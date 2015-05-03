import os
from util import *

API_KEY = '7e4592c4251cbfeff378bb585cc60c6e'
API_SECRET = 'DK1zSC6_vjhQL8ihl7b_h16mp-ZnEXHL'

current_path = os.path.dirname(__file__)


class GenderName:

    NAMES_PATH = current_path + '/data/names_INE.data'
    SURNAMES_PATH = current_path + '/data/surnames_INE.data'
    NAME_SURNAME_PATH = current_path + '/data/surnames_names_INE.data'

    __names, __name_surname = {}, {}
    __surnames = []

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
            self.__names[line[0]] = line[2]

    def _load_surnames(self):
        """
        :return: a list of Spanish surnames
        Source: Instituto Nacional de Estadística (INE)
        """
        with open(self.SURNAMES_PATH) as file:
            self.__surnames = [surname.rstrip() for surname in file.readlines()]

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
            self.__name_surname[line[0]] = line[1]

    def get_gender_by_fullname(self, fullname):
        """
        :param fullname:
        :return: gender of the given fullname and confidence
        """
        # Lower case and strip accents and punctuation
        fullname_stripped = strip_punctuation(strip_accents(fullname.lower()))
        fullname_list = fullname_stripped.split()
        result = dict()
        result['fullname_given'] = fullname
        if len(fullname_list) <= 1:
            # if just one word (name, surname or whatever)
            result['gender'] = 'unknown'
            return result
        else:
            # determine full first name (normal or compound)
            firstname, surnames = [], []
            if not self._first_word_is_name(fullname_list[0], result, firstname):
                return result
            # iterate through the rest of words if we have a name
            index = self._determine_firstname(fullname_list, firstname)
            # names finished, continue with index i determining surnames
            self._determine_surnames(fullname_list, surnames, result, index)
            if 'gender' in result:  # return result if any unknown surname
                return result
            result['firstname'] = firstname
            result['surnames'] = surnames
            result = self._determine_gender_confidence(firstname, result)
            return result

    def _first_word_is_name(self, firstword, result, firstname):
        """
        :param firstword: first word of full name
        :param result: dict of results
        :return: True if it's a name, False if not
        """
        if firstword not in self.__names:
            # check if first word is a name, if not save 'unknown'
            result['gender'] = 'unknown'
            return False
        else:
            firstname.append(firstword)
            return True

    def _determine_firstname(self, fullname_list, firstname):
        """
        Iterate through the rest of words if we have a name
        :param fullname_list: word list of fullname given
        :param firstname: variable to store first name
        :return: next index of fullname_list to be analysed
        """
        for index in range(1, len(fullname_list)):  # skip first word
            item = fullname_list[index]
            if item in self.__names:
                if item in self.__name_surname:
                    if float(self.__name_surname[item]) <= 0.5: firstname.append(item)
                    else: break
                else: firstname.append(item)
            else: break
        return index

    def _determine_surnames(self, fullname_list, surnames, result, index):
        """
        Indetifies surnames from fullname given
        :param fullname_list: word list of fullname given
        :param surnames: variable to store surnames
        :param result: dict of results
        :param index: Position in fullname_list
                      from where start looking for surnames
        """
        cache_surname = []  # for more-than-one-word surnames (i.e: de la rosa)
        for index in range(index, len(fullname_list)):
            item = fullname_list[index]
            # check if it's a valid surname
            if not cache_surname and self._add_valid_surname(item, result, surnames):
                index += 1
                break
            else:
                cache_surname.append(item)
                if self._add_valid_surname(' '.join(cache_surname), result, surnames):
                    index += 1
                    break
        # Insert the rest of surnames whether they are real or not
        for index in range(index, len(fullname_list)):
            item = fullname_list[index]
            surnames.append(item)


    def _add_valid_surname(self, word, result, surnames):
        """
        check if word is a valid surname
        :param word: word analysed
        :param result: dict of results
        :return: True if it's valid surname, False if not
        """
        if len(list(filter(lambda x: word == x, self.__surnames))) > 0:
            surnames.append(word)
            if 'gender' in result:
                del result['gender']
            return True
        else:
            result['gender'] = 'unknown'
            return False

    def _determine_gender_confidence(self, firstname, result):
        """
        Gets gender and confidence based on firstname
        :param firstname: variable to store first name
        :param result: dict of results
        :return:
        """
        firstname_str = ' '.join(firstname)
        name_confidence_male = self.__names[firstname_str] \
            if firstname_str in self.__names else 'unknown'
        if name_confidence_male == 'unknown':
            result['gender'] = 'unknown'
            return result
        elif float(name_confidence_male) > 0.6:
            result['gender'] = 'male'
            result['confidence'] = name_confidence_male
        elif 1 - float(name_confidence_male) > 0.6:
            result['gender'] = 'female'
            result['confidence'] = 1 - float(name_confidence_male)
        return result