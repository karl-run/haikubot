import hashlib

from colorharmonies import Color
import colorharmonies as color


def string_to_color_hex(string):
    return '#' + hex(int(hashlib.md5(string.encode('utf-8')).hexdigest(), 16) % 16777215) \
        .replace('0x', '') \
        .rjust(6, '0')


def complementary_color(my_hex):
    if my_hex[0] == '#':
        my_hex = my_hex[1:]
    rgb = (my_hex[0:2], my_hex[2:4], my_hex[4:6])
    comp = ['%02X' % (255 - int(a, 16)) for a in rgb]
    return '#' + ''.join(comp)


def complementary_colormap(my_hex):
    if my_hex[0] == '#':
        my_hex = my_hex[1:]
    rgb = list(map(lambda c: int(c, 16), [my_hex[0:2], my_hex[2:4], my_hex[4:6]]))
    rgb_array = Color(rgb, "", "")
    comp = list(map(lambda c: Color(c, "", ""), color.splitComplementaryColor(rgb_array)))
    nested_list = [analogus(c) for c in comp]
    return [x for sublist in nested_list for x in sublist]


def analogus(input_color):
    return list(map(lambda c: '#' + ''.join(['%02X' % a for a in c]), color.analogousColor(input_color)))
