import random
import string



def generate_orderID():
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=30))

    return random_string

