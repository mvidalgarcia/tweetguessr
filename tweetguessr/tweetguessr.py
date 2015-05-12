import json
import os
from random import randint
import operator
from gender_name import GenderName
from util import *

current_path = os.path.dirname(__file__)
TWEETS_PATH = current_path + '/data/geolocated_asturias.json'
SAMPLE_PATH = current_path + '/data/sample.json'
MALE_TABLE_PATH = current_path + '/data/male_table.data'
FEMALE_TABLE_PATH = current_path + '/data/female_table.data'
obj = GenderName()

'''
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
'''

'''
print(obj.get_gender_by_fullname('Marco Antonio Vidal García'))
print(obj.get_gender_by_fullname('Jose Maria Gutiérrez Calleja'))
print(obj.get_gender_by_fullname('Bienvenido Pérez'))
print(obj.get_gender_by_fullname('Kevin José de la Rosa Pérez'))
print(obj.get_gender_by_fullname('Fernando Móntañes'))
print(obj.get_gender_by_fullname('Jose Ramón'))
print(obj.get_gender_by_fullname('Pepe Juan'))
print(obj.get_gender_by_fullname('Petra Z. Ral'))
print(obj.get_gender_by_fullname('Andrea Fernandez♥'))
print(obj.get_gender_by_fullname('María José Fernández Andetxaga'))
print(obj.get_gender_by_fullname('María José de la rosa perez'))
print(obj.get_gender_by_fullname('Javier Alvarez-Buylla Escobar'))
print(obj.get_gender_by_fullname('Isa Noval'))
'''


def generate_male_female_sets(face_recognition=False):
    male_full_user_tweets_dict = dict()
    female_full_user_tweets_dict = dict()
    with open(TWEETS_PATH) as file:
        content = file.readlines()
        count_feedback = 1  # Count to show feedback while writing
        for _ in range(0, 50):
        #for tweet in content:
            tweet = content[randint(0, len(content)-1)]
            tweet_json = json.loads(tweet)
            screen_name = tweet_json['user']['screen_name']
            name = tweet_json['user']['name']
            res = obj.get_gender_by_fullname(name)
            if face_recognition:
                # lazy evaluation, if cannot get gender by name, try to get it by face recognition
                perform_face_recognition(res, tweet_json)
            # Already have all gender results, build table
            if res['gender'] != 'unknown':
                tweet_text = tweet_json['text']
                if res['gender'] == 'male' and float(res['confidence']) >= 0.75:
                    if screen_name not in male_full_user_tweets_dict:
                        male_full_user_tweets_dict[screen_name] = [tweet_text]
                    else:
                        male_full_user_tweets_dict[screen_name].append(tweet_text)
                    count_feedback += 1
                elif res['gender'] == 'female' and float(res['confidence']) >= 0.75:
                    if screen_name not in female_full_user_tweets_dict:
                        female_full_user_tweets_dict[screen_name] = [tweet_text]
                    else:
                        female_full_user_tweets_dict[screen_name].append(tweet_text)
                    count_feedback += 1
                if count_feedback % 10000 == 0:
                    print('Writing line {} ...'.format(count_feedback))

        # Get number of tweets of each user (just for testing!)
        #_get_and_store_num_tweets(male_full_user_tweets_dict, female_full_user_tweets_dict)

        male_num_users = len(male_full_user_tweets_dict)
        female_num_users = len(female_full_user_tweets_dict)
        test_male_len = int(male_num_users*0.2)
        training_male_len = male_num_users - test_male_len
        test_female_len = int(female_num_users*0.2)
        training_female_len = female_num_users - test_female_len

        print('{} = {} + {}'.format(male_num_users, training_male_len, test_male_len))
        # Obtain fe/male test (20%) and training (80%) sets
        male_sets = _get_test_training_sets(male_full_user_tweets_dict, test_male_len)
        male_test = male_sets['test']
        print(male_sets['test'])
        male_training = male_sets['training']
        print(male_training)
        print('{} = {} + {}'.format(female_num_users, training_female_len, test_female_len))
        female_sets = _get_test_training_sets(female_full_user_tweets_dict, test_female_len)
        female_test = female_sets['test']
        print(female_test)
        female_training = female_sets['training']
        print(female_training)
        # TODO normalizador
        # Delete stopwords
        print('----')
        for user_tweets in male_training.values():
            for tweet in user_tweets:
                print(normalise(tweet))  # normalise tweet text


def _get_test_training_sets(full_user_tweets_dict, test_len):
    test_set = dict()
    while len(test_set) < test_len:
        rand_key = list(full_user_tweets_dict.keys())[randint(0, len(full_user_tweets_dict)-1)]
        test_set[rand_key] = full_user_tweets_dict[rand_key]
    # training set = full set - test set
    training_set = {k: full_user_tweets_dict[k] for k in full_user_tweets_dict if k not in test_set}
    return {'test': test_set, 'training': training_set}


def _perform_face_recognition(res, tweet_json):
    """
    Face recognition using Face++ web service: faceplusplus.com
    :param res:
    :param tweet_json:
    :return:
    """
    if res['gender'] == 'unknown':
        profile_image = tweet_json['user']['profile_image_url'].replace('_normal', '')
        face = gender_by_profile_image(profile_image)
        if face is not None and face['confidence'] > 90:
            res['gender'] = face['gender']
            res['confidence'] = face['confidence']/100


def _write_table_file(male_female_file, screen_name, res, tweet_text):
    line = '\t'.join([screen_name, res['gender'], str(res['confidence']), tweet_text])
    male_female_file.write("%s\n" % line)


def _get_and_store_num_tweets(male_full_user_tweets_dict, female_full_user_tweets_dict):
    """
    Obtain number of tweets per user and store it in hdd (no really necessary, just for tests)
    :param male_full_user_tweets_dict:
    :param female_full_user_tweets_dict:
    :return: Dict of both male and female number of tweets per user
    """
    male_user_num_tweets = _get_user_num_tweets(male_full_user_tweets_dict, gender='male')
    #sorted_male_user_num_tweets = _write_file_user_num_tweets(male_user_num_tweets, gender='male')

    female_user_num_tweets = _get_user_num_tweets(female_full_user_tweets_dict, gender='female')
    #sorted_female_user_num_tweets = _write_file_user_num_tweets(female_user_num_tweets, gender='female')

    #return {'sorted_male_user_num_tweets': sorted_male_user_num_tweets,
    #        'sorted_female_user_num_tweets': sorted_female_user_num_tweets}


def _get_user_num_tweets(full_user_tweets_dict, gender):
    """
    Gets number of tweets written by each user.
    :param full_user_tweets_dict: Dict containing user screen_name and all his/her tweets in a list
    :param gender: male or female, just because of the print feedback
    :return: Dict of user screen names and number of tweets written that exist in dataset (no sorted)
    """
    num_tweets = 0
    user_num_tweets_dict = dict()  # i.e. {'@screen_name': 533, ...}
    for k, v in full_user_tweets_dict.items():
        user_num_tweets_dict[k] = len(v)
        num_tweets += len(v)
    print('n tweets {}:'.format(gender), num_tweets)
    return user_num_tweets_dict


def _write_file_user_num_tweets(user_num_tweets, gender):
    """
    Sort decreasingly and write a new tsv file containing users (screen_name)
    and his/her number of tweets existing in the dataset
    :param user_num_tweets: female/male dict -> '@screen_name    <num_tweets>' each line
    :param gender: male or female, just because of the filename
    :return: user_num_tweets sorted decreasingly
    """
    sorted_user_num_tweets = sorted(user_num_tweets.items(), key=operator.itemgetter(1), reverse=True)
    with open(current_path + '/data/tweets_%s_users.tsv' % gender, 'w') as f:
        for item in sorted_user_num_tweets:
            line = '\t'.join([item[0], str(item[1])])
            f.write("%s\n" % line)
    return sorted_user_num_tweets


if __name__ == "__main__":
    generate_male_female_sets()