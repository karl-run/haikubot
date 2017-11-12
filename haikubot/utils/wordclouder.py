from io import BytesIO

from matplotlib.colors import LinearSegmentedColormap
from wordcloud import WordCloud

from haikubot.utils.string_cleaner import clean_characters, clean_words, camel_case_clean
from haikubot.utils.color import complementary_colormap


def generate_cloud(haiku_blob, author_color='white'):
    cmap = None if author_color == 'white' else LinearSegmentedColormap.from_list('mycmap', complementary_colormap(author_color))
    wordcloud = WordCloud(
        width=1280,
        height=720,
        background_color=author_color,
        colormap=cmap,
    )
    dirtyclean = clean_characters(haiku_blob)
    clean_blob = clean_words(camel_case_clean(dirtyclean))
    wordcloud.generate(clean_blob)

    image = wordcloud.to_image()
    faux_file = BytesIO()
    image.save(faux_file, format="PNG")
    faux_file.seek(0)

    return faux_file
