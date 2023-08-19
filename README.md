# ChatGPT Name Parser

Experimental parser of person names into first / middle / last names, initials, marital status,
profession suffix etc. The problem is framed as a 
[Named-Entity Recognition](https://en.wikipedia.org/wiki/Named-entity_recognition) (NER) task 
and solved with the use of a ChatGPT model through OpenAI's API. The main files:

- [parser.py](https://github.com/mwojnars/chatgpt-name-parser/blob/master/parser.py) - 
  main script that submits the raw names from `person_labeled.xml` to ChatGPT, parses the output and calculates performance metrics;
- [data.py](https://github.com/mwojnars/chatgpt-name-parser/blob/master/data.py) - 
  data loading and preprocessing;
- [metrics.py](https://github.com/mwojnars/chatgpt-name-parser/blob/master/metrics.py) - 
  performance metrics calculation.

## Data

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
which makes the model capable of understanding zero-shot and few-shot NLP tasks 
(the tasks it was not specifically trained for), if only a proper task description is provided at the prompt.
This enables fast prototyping for new NLP tasks, while still allowing the model to be fine-tuned in the future
or replaced with an open-source model, like [Llama](https://ai.meta.com/llama/), if an on-premise solution is needed.


## Performance Metrics

## Results


