from .pattern import Pattern

ZERO_OR_MORE = Pattern(r'*')
ONE_OR_MORE = Pattern(r'+')
ZERO_OR_ONE = Pattern(r'?')
LAZY_ZERO_OR_MORE = Pattern(r'*?')
LAZY_ONE_OR_MORE = Pattern(r'+?')
LAZY_ZERO_OR_ONE = Pattern(r'??')

def exactly(n):
    return Pattern(r'{' + str(n) + r'}')

def least(n, lazy=False):
    pattern = r'{' + str(n) + r',}'
    if lazy: pattern += r'?'
    return Pattern(pattern)

def range(n, m, lazy=False):
    pattern = r'{' + f'{n},{m}' + r'}'
    if lazy: pattern += r'?'
    return Pattern(pattern)
