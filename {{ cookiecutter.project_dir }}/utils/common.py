import random
import string

def random_str(length: int, chars: bool = True) -> str:
    choices = string.ascii_letters + string.digits
    if chars:
        choices += '!@#$%^&*()_+-='
    return ''.join(random.choices(choices, k=length))
