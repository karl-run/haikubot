import re

_COMMON_WORDS_SIMPLE = [
    'at',
    'av',
    'ble',
    'blir',
    'bli',
    'da',
    'de',
    'deg',
    'den',
    'det',
    'du',
    'eller',
    'en',
    'enn',
    'er',
    'et',
    'etter',
    'for',
    'fra',
    'få',
    'ha',
    'hadde',
    'han',
    'har',
    'hun',
    'hva',
    'ikke',
    'jeg',
    'jo',
    'kan',
    'la',
    'litt',
    'med',
    'meg',
    'men',
    'må',
    'nok',
    'nå',
    'og',
    'om',
    'på',
    'se',
    'seg',
    'skal',
    'som',
    'så',
    'til',
    'tar',
    'ut',
    'var',
    'vi',
    'vil',
    'vel',
    'å',
]

COMMON_WORDS = list(map(lambda s: '\\b{}\\b'.format(s), _COMMON_WORDS_SIMPLE))


def clean_words(text):
    remove = '|'.join(COMMON_WORDS)
    return _replace_all(text.lower(), remove, sub_with=" ")


def clean_characters(text):
    return re.sub(' +', ' ', re.compile("[^\w']|_").sub(' ', text))


def camel_case_clean(identifier):
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return ' '.join([m.group(0) for m in matches])


def _replace_all(text, remove, sub_with=" "):
    regex = re.compile(r'(' + remove + r')', flags=re.IGNORECASE)
    return re.sub(' +', ' ', regex.sub(sub_with, regex.sub(sub_with, text)))
