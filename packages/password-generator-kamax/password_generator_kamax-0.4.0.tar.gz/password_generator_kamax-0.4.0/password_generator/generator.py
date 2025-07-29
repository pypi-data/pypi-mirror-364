import random
import string

def generate_password():
    digits = random.choices(string.digits, k=8)
    symbols = random.choices(string.punctuation, k=2)
    letters = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
    ]

    password_list = digits + symbols + letters
    random.shuffle(password_list)  # Mélange pour plus de sécurité

    return ''.join(password_list)
