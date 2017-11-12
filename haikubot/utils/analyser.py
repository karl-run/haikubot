from haikubot.utils.string_cleaner import camel_case_clean, clean_characters


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
    most_ids = []
    for haiku in haikus:
        number = _haiku_to_number_of_words(haiku)
        if number >= most:
            if number > most:
                most_ids.clear()
            most = number
            most_words_haiku = haiku
            most_ids.append(haiku['id'])

    most_ids.remove(most_words_haiku['id'])

    return most_words_haiku, most, most_ids


def get_least_words_haiku(haikus):
    least = 999
    least_words_haiku = None
    least_ids = []
    for haiku in haikus:
        number = _haiku_to_number_of_words(haiku)
        if number <= least:
            if number < least:
                least_ids.clear()
            least = number
            least_words_haiku = haiku
            least_ids.append(haiku['id'])

    least_ids.remove(least_words_haiku['id'])

    return least_words_haiku, least, least_ids


def _haiku_to_longest_word(haiku):
    split = list(filter(len, camel_case_clean(clean_characters(haiku['haiku'])).split(' ')))
    return max(split, key=len)


def _haiku_to_number_of_words(haiku):
    split = list(filter(len, clean_characters(haiku['haiku']).split(' ')))
    return len(split)
