# ChatGPT Name Parser

Experimental parser of person names into first / middle / last names, initials, marital status,
profession suffix etc. The problem is framed as a 
[Named-Entity Recognition](https://en.wikipedia.org/wiki/Named-entity_recognition) (NER) task 
and solved with the use of ChatGPT invoked through OpenAI's API. The main files:

- [parser.py](https://github.com/mwojnars/chatgpt-name-parser/blob/master/parser.py) - 
  main script that submits the raw names from `person_labeled.xml` dataset to ChatGPT, 
  parses the model output and calculates performance metrics;
- [data.py](https://github.com/mwojnars/chatgpt-name-parser/blob/master/data.py) - 
  data loading and preprocessing;
- [metrics.py](https://github.com/mwojnars/chatgpt-name-parser/blob/master/metrics.py) - 
  performance metrics calculation.

## Dataset

The script uses data from [person_labeled.xml](https://github.com/mwojnars/chatgpt-name-parser/blob/master/person_labeled.xml), which is a part of the [probablepeople](https://github.com/datamade/probablepeople) library.
This dataset serves both as a source of _few-shot learning_ examples for the ChatGPT prompt,
and as a test set for calculating performance metrics on the remaining samples.

The parsing algorithm calls `gpt-3.5-turbo` model via ChatGPT API; submits a list of raw person 
names together with a detailed task description; and receives XML code that contains 
the same names, but partitioned into entities with proper XML annotations.

The following 12 types of entities are recognized:

`GivenName`, `Surname`, `MiddleName`, `FirstInitial`, `MiddleInitial`, `LastInitial`, 
`Nickname`, `PrefixMarital`, `PrefixOther`, `SuffixGenerational`, `SuffixOther`, `And`.

The number of occurrences of each entity in the dataset is shown below:

```
2350  GivenName
2338  Surname
 387  MiddleInitial
 190  MiddleName
 165  SuffixGenerational
 115  SuffixOther
 103  PrefixMarital
  97  Nickname
  86  And
  70  FirstInitial
  63  PrefixOther
  46  LastInitial
```

## Algorithm

ChatGPT was selected as the underlying NLP model because of its high performance, versatility, 
and the ease of use through the OpenAI's API. Unlike the foundational LLM models, ChatGPT was fine-tuned for dialog
and underwent a multi-stage training process that included Reinforcement Learning from Human Feedback (RLHF),
which makes the model capable of understanding zero-shot and few-shot learning tasks 
(the tasks it was not specifically trained for), if only a proper task description is provided at the prompt.
This enables fast prototyping for new NLP tasks, while still allowing the model to be fine-tuned in the future,
or replaced with an open-source model, like [Llama](https://ai.meta.com/llama/), if an on-premise solution is needed.

The most important part of the algorithm is the prompt that is submitted to ChatGPT.
The prompt is engineered in such a way that it includes: 

- a task description with a complete list of entities that should be recognized;
- a list of examples of each entity type, which serves as a few-shot learning dataset;
- a brief summary of the annotation rules and important edge cases that should be taken into account;
- a list of raw input names to be parsed in a given batch.

The prompt template is defined in the [PROMPT](https://github.com/mwojnars/chatgpt-name-parser/blob/df2509cc2d310ba5b9bcda2bed6737d95d2318f7/parser.py#L25C1-L48) 
constant in parser.py.

The parser submits up to 30 samples at a time to ChatGPT (a *batch*).
Submitting a larger batch is technically possible, but causes instability of the model output,
which tends to be broken more frequently.

Whenever the ChatGPT output looks incorrect - contains invalid tags or insufficient number of output lines -
the API call is repeated with the same input. The number of retries is limited to 10.

The choice of examples for the few-shot learning dataset appeared to be crucial for the model performance.
Initially, the examples were selected randomly from the entire dataset, but this approach resulted in a small
diversity of the set and lower performance of the parser on the test data.
The final version of the algorithm uses a more sophisticated approach, where the selection process
takes care to include a minimum predefined number of occurrences of each entity type. Specifically, the example set 
includes 40 samples and each entity type is represented by at least 5 different samples in the set.
See the `select_examples()` function in [data.py](https://github.com/mwojnars/chatgpt-name-parser/blob/df2509cc2d310ba5b9bcda2bed6737d95d2318f7/data.py#L95) for details.


## Performance Metrics

The performance was measured with the following three metrics (see [metrics.py](https://github.com/mwojnars/chatgpt-name-parser/blob/master/metrics.py)):

A. **Character-level Exact Match Accuracy** (function `calc_equal_lines`) - 
   the percentage of samples that are parsed into an exact match of the ground truth, i.e., 
   the entire output string (line) is identical character-by-character to the ground truth string for a sample.

B. **Entity-level Exact Match Accuracy** (function `calc_equal_all_labels_in_line`) - 
   like the previous metric, but compares entity labels (tags) only instead of individual characters
   between the output and the ground truth, then counts the percentage of samples whose 
   list of entity labels is identical to the ground truth list of labels.

C. **Entity-level Label Match Accuracy** (function `calc_equal_labels_in_line`) - 
   the percentage of labels in the output that are identical to the ground truth labels
   on the corresponding positions in a line (order of entities preserved),
   averaged over all ground-truth labels in all samples; complex samples (with more entities) 
   contribute more to the metric, unlike in the previous metrics which are calculated on a per-sample basis
   and then averaged over all samples.

It should be noted that ChatGPT occasionally changes the raw text of the input names, e.g.,
by adding missing dots after prefixes or initials, or by removing surrounding quotes and parentheses around nicknames. 
If this behavior is undesired, the output can be easily fixed by post-processing, which is 
not included in the current version of the parser. The metrics B and C only compare the entities' labels, 
not their contents, which makes them more robust to this type of occasional alterations in the raw text.

The metric C is treated as the primary one, because - unlike the other two - it counts accuracy 
on a per-entity, rather than per-sample, basis.


## Results

After improvements in the prompt template and hyperparameters, the parser achieves
**82.0%** accuracy of **entity recognition** as measured by the metric C on the test set.

Parsing of the entire set of approx. 3000 samples takes about 1000 seconds when batches
of 30 samples are submitted, which translates to approx. 0.33 sec per sample.
The cost of the API calls is $0.30 for a full run over the entire data set,
which is 1 cent per 100 samples.

It should be noted that the dataset is quite difficult, because it contains many types of entities
(12 in total) and many edge cases; a significant number of samples contain Asian names, 
which are more difficult to parse than the Western ones; and the dataset contains 
some obvious errors or ambiguities, like annotating "DAVID", or "HANNA", or "RYAN",  
as surnames instead of given names.

All in all, there is still large room for improvement in the algorithm:
through model fine-tuning, better choice of hyperparameters, prompt engineering, 
post-processing of the output, etc. - it's very likely the algorithm's accuracy 
could surpass 90% on this dataset after improvements.


