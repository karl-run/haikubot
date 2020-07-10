from io import BytesIO

from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np

from haikubot.utils.string_cleaner import clean_characters, clean_words, camel_case_clean
from haikubot.utils.color import string_to_color_hex

def get_authors(haikus):
  authors = []

  for haiku in haikus:
    author = haiku[2]

    if (author not in authors):
      authors.append(author)

  return authors

def set_legend(ax, line, author, ):
  leg = Legend(ax, lines[2:], ['line C', 'line D'],
             loc='lower right', frameon=False)
  ax.add_artist(leg)


def clean_graph(graph):
    maxVal = np.amax(graph)
    clean = np.delete(graph, np.argwhere(graph == maxVal))

    return np.append(clean, maxVal)

def plot_author(ax, graph, author, anonymous = True):
      clean = clean_graph(graph)
      lastX = len(clean) - 1
      maxVal = np.amax(graph)
      
      ax.plot(clean, color=string_to_color_hex(author) )
      ax.scatter(lastX, maxVal, color=string_to_color_hex(author))
      if not anonymous:
        ax.text(lastX, maxVal, s=author, color=string_to_color_hex(author), ha='right', va='bottom')


def generate_timeline(haikus, anonymous = True):
    authors = get_authors(haikus)

    graphs = np.zeros((len(haikus), len(authors)))
    current = graphs[0]

    # Checks the author of an haiku and a
    for (index, haiku) in enumerate(haikus):
      author = haiku[2]
      current[authors.index(author)] += 1
      graphs[index] = np.copy(current)

    fig = Figure(figsize=(10,  10), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-1, len(haikus) * 1.05)
    ax.set_ylim(-1, np.amax(graphs) * 1.1)
    for (index, author) in enumerate(authors):
      plot_author(ax, graphs[:, index], author, anonymous)

    ax.legend()

    faux_file = BytesIO()
    fig.savefig(faux_file, format="PNG")
    
    faux_file.seek(0)

    return faux_file
