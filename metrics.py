"""
Performance metrics for the parser.

Author: Marcin Wojnarski (github.com/mwojnars)
"""


def calc_equal_line(true, pred):
    """Fraction 0.0-1.0 of lines in the output that are strictly equal to the target."""
    return sum([1 for i in range(len(true)) if true[i] == pred[i]]) / len(true)


