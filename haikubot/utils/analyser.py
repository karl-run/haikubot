def get_longest_word_haiku(haikus):
    longest = ''
    longest_haiku = None
    for haiku in haikus:
        word = _haiku_to_longest_word(haiku)
        if len(word) > len(longest):
            longest = word
            longest_haiku = haiku

    return longest_haiku, longest


def get_most_words_haiku(haikus):
    most = 0
    most_words_haiku = None
    for haiku in haikus:
        number = _haiku_to_number_of_words(haiku)
        if number > most:
            most = number
            most_words_haiku = haiku

    return most_words_haiku, most


def get_least_words_haiku(haikus):
    most = 999
    most_words_haiku = None
    for haiku in haikus:
        number = _haiku_to_number_of_words(haiku)
        if number < most:
            most = number
            most_words_haiku = haiku

    return most_words_haiku, most


def _haiku_to_longest_word(haiku):
    clean = _clean_haiku(haiku['haiku']).split(' ')
    return max(clean, key=len)


def _haiku_to_number_of_words(haiku):
    split = _clean_haiku(haiku['haiku']).split(' ')
    return len(split)


def _clean_haiku(haiku):
    return haiku.replace('\r\n', ' ').replace('\n', ' ') \
        .replace('.', '').replace(',', '').replace('  ', ' ').strip()
