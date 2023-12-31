"""
Parser of person names into first, middle, last names, plus prefixes, suffixes etc.
The following entities are recognized:

GivenName, Surname, MiddleName, FirstInitial, MiddleInitial, LastInitial, Nickname, PrefixMarital, PrefixOther,
SuffixGenerational, SuffixOther, And

Data set:
https://github.com/datamade/probablepeople/blob/master/name_data/labeled/person_labeled.xml

Author: Marcin Wojnarski (github.com/mwojnars)
"""

import re
import time
import openai
import random
from itertools import zip_longest

from data import load_data, get_labels, count_labels, print_labels, select_examples, exclude_examples, write_to_excel
from metrics import calc_equal_lines, calc_equal_labels_in_line, calc_equal_all_labels_in_line
from mocks import mock_001


PROMPT = \
"""
You are a Named Entity Recognition (NER) tool that takes person names on input and adds XML annotations for
different parts of the name: given name, surname, initials etc. You are allowed to use the following entities:
GivenName, MiddleName, Surname, FirstInitial, MiddleInitial, LastInitial, Nickname, PrefixMarital, PrefixOther,
SuffixGenerational, SuffixOther, And.
Every subsequence of 1+ non-whitespace characters in a line must be annotated with an entity from the above list.
Example output:

{examples}

Observe that entities only include non-space characters and can only start and end on whitespace;
comma "," can be used to reverse the order of given name vs surname;
a single-word name may very well represent a surname rather than a given name;
name prefixes and suffixes can be added for marital status, generation, education, profession etc.;
initials and nicknames can be used instead, or in addition to, given names and surnames;
"&" and "and" entities can be used to join multiple names (given names, surnames) on a single line;
"Mr" should be treated as PrefixMarital not Other.

Now, when you understand the rules, parse the following list of raw names and output corresponding annotations.
Do NOT output anything else: no description, no line numbers, no bullet points. Do NOT insert any extra
characters to the raw text inside annotations, nor change existing raw characters. Input names:

{names}
"""


# list of all entities that can be used in the output, for validation checks
ENTITIES = ("GivenName MiddleName Surname FirstInitial MiddleInitial LastInitial Nickname PrefixMarital PrefixOther "
            "SuffixGenerational SuffixOther And").split()


def build_prompt(examples, names_annotated):
    """
    Build a prompt for ChatGPT. The prompt consists of a description of the task, a list of example annotated names,
    and a list of raw names to be annotated.
    """
    # remove XML tags from names_annotated
    names = [re.sub(r'</?[a-zA-Z]+>', '', name) for name in names_annotated]
    return PROMPT.format(examples='\n'.join(examples), names='\n'.join(names))
    
    
def parse_names_once(examples, names):
    """
    Parse a (small) batch of names in a single call to OpenAI API.
    This function should be called multiple times to parse a large batch of names.
    OpenAI API key must be stored in OPENAI_API_KEY environment variable.
    """
    start_time = time.time()
    
    prompt = build_prompt(examples, names)
    length = len(prompt)
    
    print(f'\nPrompt ({length} characters, approx. {int(length/3.0)} tokens):')
    print(prompt)

    # response = openai.Completion.create(engine='davinci', prompt=prompt, max_tokens=800) #, temperature=0.0, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0, stop=['\n'])
    response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[{"role": "user", "content": prompt}]) #, temperature=0.5)
    
    # print('\n\nResponse:')
    # print(response)
    
    # output = response.choices[0].text
    output = response.choices[0].message.content
    print('\n\nOutput:')
    print(output)
    
    end_time = time.time()
    print(f'\n\nTime elapsed: {end_time - start_time:.2f} seconds')
    
    output_lines = output.splitlines()
    
    return list(filter(None, [line.strip() for line in output_lines]))
    
    
def parse_names_all(examples, names, batch_size=30, max_retry=10):
    """
    Parse a (large) set of names in multiple calls to OpenAI API. Merge the results.
    """
    output = []

    for i in range(0, len(names), batch_size):
        print(f'\nParsing batch starting at {i}...')
        batch = names[i:i+batch_size]
        pred = []
        
        retry = 0
        while len(pred) != len(batch) or wrong_syntax(pred):        # retry if the output looks incomplete/incorrect
            if retry > max_retry: break
            if retry > 0: print(f'\nRetrying ({retry})...')
            
            try:
                pred = parse_names_once(examples, batch)

            except openai.error.APIError as e:
                print(f'\n\nAPI ERROR: {e}')
                print(f'Will call again after 10 seconds...')
                time.sleep(10)
                continue
            
            retry += 1

        if len(pred) != len(batch):
            print(f'\n\nWARNING: Prediction and target sets have different lengths for a batch starting at {i}: {len(pred)} vs {len(batch)}')
            if len(pred) > len(batch):
                pred = pred[:len(batch)]                  # cut `pred` to make it the same length as `batch`
            else:
                pred += [''] * (len(batch) - len(pred))   # append empty lines to make `pred` the same length as `batch`

        output += pred
    
    return output
    
    
def wrong_syntax(pred, threshold=0.1):
    """
    Return True if 10% or more samples in the ChatGPT output have incorrect syntax: no XML tags, self-closing tags,
    or the tags have wrong names.
    """
    
    # lists of labels in each line; self-closing tags are included (e.g. <GivenName/>) and treated as incorrect
    labels = [re.findall(r'<([a-zA-Z]+/?)>', line) for line in pred]
    
    # count samples with no XML tags
    no_tags = sum(1 for lbl in labels if not lbl)
    
    # count samples with wrong XML tags (other than the ones in ENTITIES)
    wrong_tags = sum(1 for lbl in labels if lbl and not all(tag in ENTITIES for tag in lbl))
    
    if no_tags + wrong_tags >= threshold * len(pred):
        print(f'\n\nWARNING: {wrong_tags} outputs with wrong XML tags + {no_tags} outputs with no proper XML tags')
        return True
    
    return False
    
    
########################################################################################################################

EXPERIMENT = '016_full'


def main():
    start_time = time.time()

    lines = load_data('person_labeled.xml')
    # print('\n'.join(lines))
    # print()
    # print_labels(lines)
    
    # select a short list of examples in a smart way, so that each label is represented by at least 5 samples
    examples = select_examples(lines, size=40, k=5)
    
    # use remaining lines as test set
    test = exclude_examples(lines, examples)
    
    # print(f'\n\nExample set ({len(examples)}):')
    # print('\n'.join(examples))
    # print_labels(examples)
    
    true, pred, _ = mock_001()
    
    true = test   # [::10]
    random.shuffle(true)
    pred = parse_names_all(examples, true)
    
    write_to_excel(true, pred, f'../experiments/out_{EXPERIMENT}.xlsx')
    
    # print predictions vs targets side by side for comparison
    print(f'\n\nPredictions ({len(pred)}) vs Targets ({len(true)}):')
    for t, p in list(zip_longest(true, pred)):
        print()
        print('pred: ', p)
        print('true: ', t)
        # print(f'{p:120}  |  {t}')
        
    # print metrics...
    print('\n\nMetrics:')
    print(f'no. of identical lines:                  {calc_equal_lines(true, pred):.1%}')
    print(f'no. of lines with all identical labels:  {calc_equal_all_labels_in_line(true, pred):.1%}')
    print(f'no. of individual identical labels:      {calc_equal_labels_in_line(true, pred):.1%}')
    
    if (len(pred) != len(true)):
        print(f'\n\nWARNING: Prediction and target sets have different lengths: {len(pred)} vs {len(true)}')

    end_time = time.time()
    print(f'\n\nSamples processed:  {len(true)}')
    print(f'Time elapsed:       {end_time - start_time:.2f} seconds')


if __name__ == '__main__':
    main()
