import json, os
from random import randint
from gender_name import GenderName

current_path = os.path.dirname(__file__)
TWEETS_PATH = current_path + '/data/geolocated_asturias.json'
SAMPLE_PATH = current_path + '/data/sample.json'
obj = GenderName()

with open(TWEETS_PATH) as file:
    content = file.readlines()
    for _ in range(0, 10):
        tweet = content[randint(0, len(content)-1)]
        tweet_json = json.loads(tweet)
        name = tweet_json['user']['name']
        print(obj.get_gender_by_fullname(name))


#print(data['created_at'])


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


#surnames = obj.fullname_gender('Pepe')
#print(names['andrea'])
#print(obj.name_surname['alonso'])
#print(len(list(filter(lambda x: 'vidal' == x, obj.surnames))))