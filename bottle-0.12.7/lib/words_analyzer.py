import re
from fuzzywuzzy import process

def split(words, separator=None):
    pos = 0
    exp = re.compile(r'\s+' if separator is None else re.escape(separator))
    while True:
        m = exp.search(words, pos)
        if not m:
            if (pos < len(words)) or (separator is not None):
                yield words[pos:]
            break
        if (pos < m.start()) or (separator is not None):
            yield words[pos:m.start()]
        pos = m.end()


def recommend(word, words):
    return process.extract(word, words, limit=1)[0][0]
