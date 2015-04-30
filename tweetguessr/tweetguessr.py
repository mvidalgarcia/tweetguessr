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
        print(obj.fullname_gender(name))


#print(data['created_at'])

'''
print(obj.fullname_gender('Marco Vidal García'))
print(obj.fullname_gender('Jose Maria Gutiérrez Calleja'))
print(obj.fullname_gender('Bienvenido Pérez'))
print(obj.fullname_gender('Kevin José de la Rosa Pérez'))
print(obj.fullname_gender('Fernando Móntañes'))
print(obj.fullname_gender('saul arias tomás'))
print(obj.fullname_gender('Jose Ramón'))
print(obj.fullname_gender('Pepe Juan'))
'''
print(obj.fullname_gender('Andrea Fernandez♥'))


#surnames = obj.fullname_gender('Pepe')
#print(names['andrea'])
#print(obj.name_surname['alonso'])
#print(len(list(filter(lambda x: 'vidal' == x, obj.surnames))))