# PyComplete

An autocomplete tool written in Python. This is largely a proof of concept.
I might rewrite in C++ if I get this working, might not tho, who knows.


## Installation
```
pip install pycomplete
```

## TODOS
- [x] Add caching/save-file for a PyComplete instances
- [ ] Figure out asymptotic runtimes for `trie.py` and `pycomplete.py` 

### Notes
- All of our runtime analyses are expected runtimes, not worst-case runtimes 
    - **NOTE**: Sometimes my analyses get weird and I try to explain what I did lol
- I think I want to be more consistent with the exceptions I raise.
 