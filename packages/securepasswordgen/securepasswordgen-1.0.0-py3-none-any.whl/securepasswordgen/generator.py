import string
import secrets

def generate_password(length=16, use_upper=True, use_lower=True, use_digits=True, use_symbols=True):
    if not any([use_upper, use_lower, use_digits, use_symbols]):
        raise ValueError("At least one character set must be enabled.")

    charset = ''
    if use_upper:
        charset += string.ascii_uppercase
    if use_lower:
        charset += string.ascii_lowercase
    if use_digits:
        charset += string.digits
    if use_symbols:
        charset += string.punctuation

    return ''.join(secrets.choice(charset) for _ in range(length))
