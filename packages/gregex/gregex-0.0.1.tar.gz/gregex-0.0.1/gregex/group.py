from .pattern import Pattern

class Group:
    def __init__(self, pattern=None, name=None, non_grouping=False):
        self.name = None
        self.data = pattern.pattern if pattern else ''
        if non_grouping:
            self.name = ''
            self.data = r'?:' + self.data
        elif name:
            self.name = name
            self.data = f'?P<{name}>' + self.data

    def __add__(self, other):
        return Pattern(self.pattern + other.pattern)

    @property
    def pattern(self):
        return f'({self.data})'

GROUP_ALL = Group(pattern=Pattern(r'?s:.'))