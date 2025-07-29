import random
import string

def generate_password(length=12):
    if length < 4:
        raise ValueError("La longueur minimale est 4 caractères.")

    # Obligatoire : au moins 1 chiffre, 1 symbole, 1 majuscule, 1 minuscule
    required = [
        random.choice(string.digits),
        random.choice(string.punctuation),
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
    ]

    # Reste des caractères (aléatoires)
    remaining_length = length - len(required)
    all_chars = string.ascii_letters + string.digits + string.punctuation
    remaining = random.choices(all_chars, k=remaining_length)

    password_list = required + remaining
    random.shuffle(password_list)

    return ''.join(password_list)
