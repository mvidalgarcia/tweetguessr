import json
import os
import collections
from random import randint
import operator
from gender_name import GenderName
from util import *

current_path = os.path.dirname(__file__)
TWEETS_PATH = current_path + '/data/geolocated_asturias.json'
SAMPLE_PATH = current_path + '/data/sample.json'
MALE_TABLE_PATH = current_path + '/data/male_table.data'
FEMALE_TABLE_PATH = current_path + '/data/female_table.data'
gender_name = GenderName()

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


def classify_tweets(face_recognition=False, min_confidence=0.75):
    print('Classifying tweets by gender name...')
    male_full_user_tweets_dict = dict()
    female_full_user_tweets_dict = dict()
    with open(TWEETS_PATH) as file:
        content = file.readlines()
        count_feedback = 1  # Count to show feedback while writing
        #for _ in range(0, 100):
        for tweet in content:
           # tweet = content[randint(0, len(content)-1)]
            tweet_json = json.loads(tweet)
            screen_name = tweet_json['user']['screen_name']
            name = tweet_json['user']['name']
            res = gender_name.get_gender_by_fullname(name)
            if face_recognition:
                # lazy evaluation, if cannot get gender by name, try to get it by face recognition
                perform_face_recognition(res, tweet_json)
            # Already have all gender results, build table
            if res['gender'] != 'unknown':
                tweet_text = tweet_json['text']
                if res['gender'] == 'male' and float(res['confidence']) >= min_confidence:
                    if screen_name not in male_full_user_tweets_dict:
                        male_full_user_tweets_dict[screen_name] = {tweet_text}
                    else:
                        male_full_user_tweets_dict[screen_name].add(tweet_text)
                    count_feedback += 1
                elif res['gender'] == 'female' and float(res['confidence']) >= min_confidence:
                    if screen_name not in female_full_user_tweets_dict:
                        female_full_user_tweets_dict[screen_name] = {tweet_text}
                    else:
                        female_full_user_tweets_dict[screen_name].add(tweet_text)
                    count_feedback += 1
                if count_feedback % 10000 == 0:
                    print('\tWriting tweet line {} ...'.format(count_feedback))

        # Get number of tweets of each user (just for testing!)
        #_get_and_store_num_tweets(male_full_user_tweets_dict, female_full_user_tweets_dict)

    return male_full_user_tweets_dict, female_full_user_tweets_dict


def generate_sets(male_tweets_dict, female_tweets_dict, percentage_test):
    """
    Gets fe/male test (20%) and training (80%) sets
    :param male_tweets_dict: Male tweets selected
    :param female_tweets_dict: Female tweets selected
    :param percentage_test: Percentage of members in test set in relation to full set
    :return: Fe/male training and test sets
    """

    male_num_users = len(male_tweets_dict)
    female_num_users = len(female_tweets_dict)
    test_male_len = int(male_num_users * percentage_test)
    test_female_len = int(female_num_users * percentage_test)

    print('Generating male training and test sets...')
    male_test, male_training = _get_test_training_sets(male_tweets_dict, test_male_len)
    #_print_sets_size_feedback(male_training, male_test, male_num_users, test_male_len, gender='Male')
    print('Generating female training and test sets...')
    female_test, female_training = _get_test_training_sets(female_tweets_dict, test_female_len)
    #_print_sets_size_feedback(female_training, female_test, female_num_users, test_female_len, gender='Female')
    return {'male_training': male_training, 'male_test': male_test,
            'female_training': female_training, 'female_test': female_test}


def build_lexicon(male_training, female_training, llr_threshold=0.5):
    """
    Builds lexicon from training sets using LLR function
    :param male_training:
    :param female_training:
    :return:
    """
    print('Getting word frequencies...')
    # Get word frequencies
    male_words_freq, male_word_count = _get_word_freq(male_training)
    #print(sorted(male_words_freq.items(), key=operator.itemgetter(1), reverse=True))
    #print(male_word_count)
    female_words_freq, female_word_count = _get_word_freq(female_training)
    #print(sorted(female_words_freq.items(), key=operator.itemgetter(1), reverse=True))
    #print(female_word_count)

    all_words = set(male_words_freq.keys()) | set(female_words_freq.keys())

    lexicon = dict()
    print('Building lexicon...')
    for word in all_words:
        #if 500 < male_words_freq[word] < 2000:  # TODO: Reconsider this doing it better
            lexicon[word] = root_log_likelihood_ratio(male_words_freq[word], female_words_freq[word],
                                                      male_word_count, female_word_count)
    return _trim_lexicon(lexicon, llr_threshold)


def _trim_lexicon(lexicon, threshold):
    """
    Keep just the most meaningful terms. Those >= 0.5 or <= -0.5
    :param lexicon: initial lexicon
    :return: trimmed lexicon
    """
    trimmed_lexicon = {word: llr for word, llr in lexicon.items() if llr >= threshold or llr <= -threshold}
    return trimmed_lexicon


def _get_word_freq(training_set):
    """
    Computes the frequency of each word and total number of words in a training set
    :param training_set: Female/male training set
    :return: Dict of words frequencies (decreasingly sorted) and total number of words in set
    """
    words_freq = collections.defaultdict(int)
    word_count = 0
    for user_tweets in training_set.values():
        for tweet in user_tweets:
            for word in normalise(tweet).split():  # normalise tweet text
                words_freq[word] += 1
                word_count += 1
    return words_freq, word_count


def _print_sets_size_feedback(training_set, test_set, num_users, test_len, gender):
    """
    Print feedback about training/test sets size and content
    """
    print('{} tweets {} = training {} + test {}'.format(gender, num_users, num_users - test_len, test_len))
    print(training_set)
    print(test_set)


def _get_test_training_sets(full_user_tweets_dict, test_len):
    test_set = dict()
    while len(test_set) < test_len:
        rand_key = list(full_user_tweets_dict.keys())[randint(0, len(full_user_tweets_dict)-1)]
        test_set[rand_key] = full_user_tweets_dict[rand_key]
    # training set = full set - test set
    training_set = {k: full_user_tweets_dict[k] for k in full_user_tweets_dict if k not in test_set}
    return test_set, training_set


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


def perform_tests(lexicon, male_test, female_test):

    print('Performing tests...')
    recall_males, precision_males = perform_test(lexicon, male_test, 'male')
    recall_females, precision_females = perform_test(lexicon, female_test, 'female')
    print("Males:\n\tRecall: {}\tPrecision: {}".format(recall_males, precision_males))
    print("Females:\n\tRecall: {}\tPrecision: {}".format(recall_females, precision_females))


def perform_test(lexicon, test_set, gender):
    """
    Calculates recall and precision from test_set
    :param lexicon:
    :param test_set:
    :param gender:
    :return: recall and precision
    """
    # TODO: Consider accumulate LLR in a variable
    male_tweets, female_tweets, unclassified = 0, 0, 0
    for user_tweets in test_set.values():
        for tweet in user_tweets:
            male_words, female_words = 0, 0
            for word in normalise(tweet).split():  # normalise tweet text
                if word in lexicon:
                    if lexicon[word] > 0:
                        male_words += 1
                    else:
                        female_words += 1
            if male_words == female_words:
                unclassified += 1
            if male_words > female_words:
                male_tweets += 1
            else:
                female_tweets += 1
    # Get results
    recall = (male_tweets + female_tweets) / (male_tweets + female_tweets + unclassified)
    precision = (male_tweets if gender is 'male' else female_tweets) / (male_tweets + female_tweets)
    return recall, precision


def main():
    male_tweets_dict, female_tweets_dict = classify_tweets()
    sets = generate_sets(male_tweets_dict, female_tweets_dict, percentage_test=0.2)
    lexicon = build_lexicon(sets['male_training'], sets['female_training'], llr_threshold=0.5)
    perform_tests(lexicon, sets['male_test'], sets['female_test'])

if __name__ == "__main__":
    main()