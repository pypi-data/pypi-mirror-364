from .pattern import Pattern

class Char:
    def __init__(self, char):
        self.data = char

    def __add__(self, other):
        return Pattern(self.pattern + other.pattern)

    @property
    def pattern(self):
        return self.data

TAB = Char(r'\t')
NEWLINE = Char(r'\n')
NON_NEWLINE = Char(r'.')
BACKSLASH = Char(r'\\')
# [a-zA-Z_0-9]
WORD = Char(r'\w')
# [^a-zA-Z_0-9]
NON_WORD = Char(r'\W')
# begin the match at a word boundary
WORD_BOUNDARY = Char(r'\b')
WHITESPACE = Char(r'\s')
NON_WHITESPACE = Char(r'\S')
# [0-9]
DIGIT = Char(r'\d')
NON_DIGIT = Char(r'\D')
MATCH_BEGIN = Char(r'^')
MATCH_END = Char(r'$')