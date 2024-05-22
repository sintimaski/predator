import string
import random


def generate_random_string(length=40):
    # Define the character set
    characters = string.ascii_letters + string.digits

    # Generate the random string
    random_string = "".join(random.choice(characters) for _ in range(length))

    return random_string


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
