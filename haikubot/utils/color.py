import hashlib


def string_to_color_hex(string):
    return '#' + hex(int(hashlib.md5(string.encode('utf-8')).hexdigest(), 16) % 16777215) \
        .replace('0x', '') \
        .rjust(6, '0')
