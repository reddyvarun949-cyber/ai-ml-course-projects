# Python Basics for Data Science

Topic: Python & Data

## Why Python
Python is the most common language for data science and machine learning. Its syntax is short and readable, and it has
a huge set of free libraries: NumPy for arrays, pandas for tables, Matplotlib for charts and scikit-learn for machine
learning. You can run Python in a terminal, in a script file, or in a Jupyter notebook where code and explanations sit
side by side.

## Variables and data types
A variable is a name that points to a value. You do not declare the type; Python works it out. The basic types are
integers (`7`), floats (`3.14`), strings (`"hello"`) and booleans (`True` / `False`). Use `type(x)` to check what a
value is. Converting between types is common when reading data: `int("42")` turns text into a number, and
`str(42)` turns a number into text.

## Lists and dictionaries
A list holds an ordered collection: `scores = [72, 88, 95]`. You can index it (`scores[0]`), slice it (`scores[1:]`)
and add items with `append`. A dictionary stores key-value pairs: `student = {"name": "Asha", "age": 21}`. Dictionaries
are everywhere in real projects because JSON data from web APIs and language models arrives as nested dictionaries
and lists.

## Loops, conditions and comprehensions
A `for` loop repeats code for each item, and `if` / `elif` / `else` chooses what to run. A list comprehension builds a
new list in one line: `squares = [n * n for n in range(5)]`. Comprehensions are shorter than loops, but keep them
simple; if a comprehension needs two conditions and a nested loop, a normal loop is easier to read.

## Functions
A function packages code you want to reuse. Define it with `def`, give it parameters and return a result:

```python
def average(numbers):
    return sum(numbers) / len(numbers)
```

Good functions do one job, have a clear name and include a short docstring explaining what they expect and return.

## Handling errors
When something goes wrong Python raises an exception, for example `ValueError` or `FileNotFoundError`. Wrap risky
code in `try` / `except` so your program can show a friendly message instead of crashing. Do not hide every error with
a bare `except:`; catch the specific exception you expect.

## Files and JSON
Open files with `with open("data.txt") as f:` so the file is closed automatically. The `json` module converts between
Python dictionaries and JSON text: `json.load` reads a file and `json.dumps` turns a dictionary into a string.
