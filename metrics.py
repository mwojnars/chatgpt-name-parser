"""
Performance metrics for the parser.

Author: Marcin Wojnarski (github.com/mwojnars)
"""


from data import get_labels


def calc_equal_lines(true, pred):
    """Fraction 0.0-1.0 of lines in the output that are strictly equal to the target."""
    return sum(t == p for t, p in zip(true, pred)) / len(true)


def calc_equal_all_labels_in_line(true, pred):
    """Fraction 0.0-1.0 of lines in the output that have all labels identical to the target."""
    return sum(get_labels(t) == get_labels(p) for t, p in zip(true, pred)) / len(true)


def calc_equal_labels_in_line(true, pred):
    """Fraction 0.0-1.0 of labels in the output that are identical to the target label on the same position in line."""
    return (sum(t == p for t_line, p_line in zip(true, pred) for t, p in zip(get_labels(t_line), get_labels(p_line)))
            / sum([len(get_labels(t_line)) for t_line in true]))

