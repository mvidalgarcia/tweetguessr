import json
import os
from random import randint
from gender_name import GenderName
from util import *

current_path = os.path.dirname(__file__)
TWEETS_PATH = current_path + '/data/geolocated_asturias.json'
SAMPLE_PATH = current_path + '/data/sample.json'
obj = GenderName()

with open(TWEETS_PATH) as file:
    content = file.readlines()
    for _ in range(0, 10):
        tweet = content[randint(0, len(content)-1)]
        tweet_json = json.loads(tweet)
        print(tweet_json['user']['profile_image_url'].replace('_normal', ''))
        name = tweet_json['user']['name']
        res = obj.get_gender_by_fullname(name)
        # lazy evaluation, if cannot get gender by name, try to get it by face recognition
        if res['gender'] == 'unknown':
            face = gender_by_profile_image(tweet_json['user']['profile_image_url'].replace('_normal', ''))
            if face is not None and face['confidence'] > 90:
                res['gender'] = face['gender']
                res['confidence'] = face['confidence']/100
        print(res)


print(obj.get_gender_by_fullname('Marco Antonio Vidal García'))
'''
print(obj.get_gender_by_fullname('Jose Maria Gutiérrez Calleja'))
print(obj.get_gender_by_fullname('Bienvenido Pérez'))
print(obj.get_gender_by_fullname('Kevin José de la Rosa Pérez'))
print(obj.get_gender_by_fullname('Fernando Móntañes'))
print(obj.get_gender_by_fullname('Jose Ramón'))
print(obj.get_gender_by_fullname('Pepe Juan'))
'''
print(obj.get_gender_by_fullname('Petra Z. Ral'))
print(obj.get_gender_by_fullname('Andrea Fernandez♥'))
print(obj.get_gender_by_fullname('María José Fernández Andetxaga'))
print(obj.get_gender_by_fullname('María José de la rosa perez'))
print(obj.get_gender_by_fullname('Javier Alvarez-Buylla Escobar'))

#surnames = obj.fullname_gender('Pepe')
#print(names['andrea'])
#print(obj.name_surname['alonso'])
#print(len(list(filter(lambda x: 'vidal' == x, obj.surnames))))

