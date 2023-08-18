"""
Data loading and preprocessing.

Author: Marcin Wojnarski (github.com/mwojnars)
"""

import re
import random
from collections import Counter


def data_cleaning(xml):
    """
    Drop <NameCollection> and <Name> tags. Remove empty lines. Strip leading and trailing spaces.
    Return a list of lines.
    """
    
    xml = xml.replace('<NameCollection>', '')
    xml = xml.replace('</NameCollection>', '')
    xml = xml.replace('<Name>', '')
    xml = xml.replace('</Name>', '')
    xml = xml.replace('&amp;', '&')
    
    # strip leading and trailing spaces in each line; filter out empty lines
    return list(filter(None, [line.strip() for line in xml.split('\n')]))


def get_labels(line):
    """
    Return a list of all XML labels (tags) occurring in the given line, e.g. Name or GivenName. Ignore closing tags.
    """
    return re.findall(r'<([a-zA-Z]+)>', line)


def load_data(filename):
    """
    Load data from XML file. Remove unnecessary tags and convert to a list of lines.
    """
    with open(filename, 'r') as f:
        xml = f.read()
    return data_cleaning(xml)


def count_labels(lines):
    """
    Make a list of all XML labels occurring in the data set represented by a list of lines.
    Return a Counter object.
    """
    labels = Counter()
    for line in lines:
        labels.update(get_labels(line))
    
    return labels


def print_labels(lines):
    """
    Count all XML labels occurring in the dataset and print a list sorted by counts.
    """
    labels = count_labels(lines)
    print('\n'.join([f'{count:4}  {label}' for label, count in labels.most_common()]))


def split_data(lines, stride=100):
    """
    Split the data set into "example" and "test" sets. The "example" set is small and intended for inclusion
    in ChatGPT prompt to let the model understand the task. The "test" set contains remaining samples
    and is used for benchmarking of the ChatGPT-based extraction procedure.
    The stride parameter controls the size of the "example" set: every stride-th sample is included.
    There is no randomization because the data set has a logical order (different types of samples are grouped together)
    and we want to take a sample from each group to make the "example" set representative, more or less.
    """
    lines_example = lines[::stride]
    lines_test = []
    
    # pick all elements from `lines` except [::stride] indices and put them into `lines_test`
    for i in range(len(lines)):
        if i % stride != 0:
            lines_test.append(lines[i])
    
    return lines_example, lines_test


def exclude_examples(lines, examples):
    """
    Another way to split the data set into "example" and "test" sets: given `examples`, remove their literal occurrences
    from the `lines` data set and return as a new list of test lines.
    """
    examples = set(examples)
    return [line for line in lines if line not in examples]


def select_examples(lines, size=30, k=3, seed=12345):
    """
    Select `size` random examples from `lines` and return them as a list of lines.
    The selection is done in such a way that each label (entity type) is represented by at least `k` samples,
    starting with the least frequent label.
    """
    labels = count_labels(lines)
    picked = Counter()                  # how many examples of each label have been picked so far into `output`
    output = set()
    rand = random.Random(seed)
    
    # group lines by the labels that occur in them
    samples_by_label = {label: [] for label in labels}
    for line in lines:
        for label in get_labels(line):
            samples_by_label[label].append(line)
        
    for label, count in reversed(labels.most_common()):
        if len(output) >= size:
            break
        remain = max(0, k - picked[label])          # how many more samples of this label are needed

        while remain:
            # pick a random sample containing this label
            sample = rand.choice(samples_by_label[label])
            if sample in output:
                continue

            # update picked[] counter for all the labels occurring in this sample
            for lbl in get_labels(sample):
                picked[lbl] += 1
            
            output.add(sample)
            remain -= 1
    
    # if there are still not enough samples, pick the remaining ones randomly
    while len(output) < size:
        sample = rand.choice(lines)
        if sample not in output:
            output.add(sample)
    
    return sorted(output)
