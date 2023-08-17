"""
Parser of person names into first, middle, last names, plus prefixes, suffixes etc.

Data set:
https://github.com/datamade/probablepeople/blob/master/name_data/labeled/person_labeled.xml
"""

import re
import time
import openai

from data import load_data, count_labels, print_labels, split_data, select_examples, exclude_examples


EXAMPLES = \
"""
""".strip().splitlines()

PROMPT = \
"""
You are a Named Entity Recognition (NER) tool that takes person names on input and adds XML annotations for
different parts of the name: given name, surname, initials etc. You are allowed to use the following entities:
GivenName, Surname, MiddleName, FirstInitial, MiddleInitial, LastInitial, Nickname, PrefixMarital, PrefixOther,
SuffixGenerational, SuffixOther, And.
Every sequence of 1+ non-whitespace characters must be annotated with an entity. Example output:

{examples}

Observe that entities can only start/end on whitespace; comma "," can be used to reverse the order of the given name vs surname;
name prefixes and suffixes can be added for marital status, generation, education, profession etc.;
initials and nicknames can be used instead, or in addition to, given names and surnames;
"&" and "and" entities can be used to join multiple names (given names, surnames) on a single line.

Now, when you understand the rules, parse the following list of raw names and output corresponding annotations.
Do NOT output anything else: no description, no line numbers, no bullet points. Do NOT insert any extra
characters to the raw text inside annotations, nor change existing raw characters. Input names:

{names}
"""
# Put the output XML inside ```...```.


def build_prompt(examples, names_annotated):
    """
    Build a prompt for ChatGPT. The prompt consists of a description of the task, a list of example annotated names,
    and a list of raw names to be annotated.
    """
    # remove XML tags from names_annotated
    names = [re.sub(r'</?[a-zA-Z]+>', '', name) for name in names_annotated]
    return PROMPT.format(examples='\n'.join(examples), names='\n'.join(names))
    
    
def parse_names_openai(examples, names):
    """
    Parse names using OpenAI API.
    OpenAI API key must be stored in OPENAI_API_KEY environment variable.
    """
    start_time = time.time()
    
    prompt = build_prompt(examples, names)
    length = len(prompt)
    
    print(f'\n\nPrompt ({length} characters, approx. {int(length/3.5)} tokens):')
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
    
    return output
    
    
########################################################################################################################


def main():
    lines = load_data('person_labeled.xml')
    print('\n'.join(lines))
    print()
    
    print_labels(lines)
    
    # select a short list of examples in a smart way, so that each label is represented by at least 4 samples
    examples = select_examples(lines, size=30, k=4)
    
    # use remaining lines as test set
    test = exclude_examples(lines, examples)
    
    # examples, test = split_data(lines)
    print(f'\n\nExample set ({len(examples)}):')
    print('\n'.join(examples))
    print_labels(examples)
    # print('\n\nTest set:')
    # print('\n'.join(test))

    output = parse_names_openai(examples, test[::50])
    

if __name__ == '__main__':
    main()
