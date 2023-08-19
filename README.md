# ChatGPT Name Parser

Experimental parser of person names into first/middle/last names, initials, marital status,
profession suffix etc. Uses ChatGPT API. The main files:
- [parser.py](https://github.com/mwojnars/chatgpt-name-parser/blob/master/parser.py) - 
  main script that parses the names from `person_labeled.xml` and calculates performance metrics;
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

The following 12 entities are recognized:

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


