import random


def random_key(dictionary):
    """
    Select a random key from a dictionary
    :param dictionary:
    :return key:
    """
    keys = list(dictionary.keys())
    random_key = random.choice(keys)
    return random_key


def find_key(dictionary, value):
    """
    Given a dictionary and value, return the key
    :param dictionary:
    :param value:
    :return key:
    """
    for key, val in dictionary.items():
        if val == value:
            return key
    return None
