from .char import WHITESPACE, NON_WHITESPACE
from .pattern import Pattern

class Set:
    def __init__(self, pattern=None):
        self.data = pattern.pattern if pattern else ''

    def add_char(self, char):
        self.data += char
        return self

    def add_range(self, start, end):
        self.data += f'{start}-{end}'
        return self

    def __add__(self, other):
        return Pattern(self.pattern + other.pattern)

    @property
    def pattern(self):
        return f'[{self.data}]'

SET_ALL = Set(pattern=Pattern(f'{WHITESPACE.pattern}{NON_WHITESPACE.pattern}'))

class ReverseSet(Set):
    def __init__(self):
        self.data = '^'
