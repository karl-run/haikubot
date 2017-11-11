import re

_COMMON_WORDS_SIMPLE = [
    'at',
    'av',
    'ble',
    'da',
    'de',
    'den',
    'det',
    'du',
    'er',
    'et',
    'en',
    'etter',
    'for',
    'fra',
    'hadde',
    'han',
    'har',
    'hun',
    'ikke',
    'jeg',
    'kan',
    'nå',
    'må',
    'litt',
    'med',
    'men',
    'og',
    'om',
    'på',
    'seg',
    'som',
    'så',
    'til',
    'ut',
    'var',
    'vi',
    'vil',
    'å',
    'hva',
    'ha',
    'meg',
    'blir',
    'skal',
    'se',
    'deg',
    'eller',
]

COMMON_WORDS = list(map(lambda s: '\\b{}\\b'.format(s), _COMMON_WORDS_SIMPLE))
wordcloud_blacklist = dict(zip(COMMON_WORDS, [' '] * len(COMMON_WORDS)))


def clean_words(text):
    remove = '|'.join(COMMON_WORDS)
    return _replace_all(text.lower(), remove, sub_with=" ")


def clean_characters(text):
    return re.sub(' +', ' ', re.compile("[^\w']|_").sub(' ', text))


def _replace_all(text, remove, sub_with=" "):
    regex = re.compile(r'(' + remove + r')', flags=re.IGNORECASE)
    return re.sub(' +', ' ', regex.sub(sub_with, regex.sub(sub_with, text)))


def camel_case_clean(identifier):
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return ' '.join([m.group(0) for m in matches])
