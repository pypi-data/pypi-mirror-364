class Pattern:
    def __init__(self, pattern):
        self.pattern_ = pattern

    def __add__(self, other):
        return Pattern(self.pattern + other.pattern)

    @property
    def pattern(self):
        return self.pattern_