# NLP Fundamentals

Topic: NLP & GenAI

## What NLP is
Natural language processing (NLP) is the part of AI that works with human language: classifying reviews as positive or
negative, detecting spam, extracting names from documents, translating, summarising and answering questions. Computers
need numbers, so the first problem in NLP is always how to turn text into numbers without losing its meaning.

## Cleaning and tokenisation
A typical pipeline lowercases the text, removes extra spaces and odd symbols, and then splits it into **tokens**, usually
words or pieces of words. **Stop words** such as "the", "is" and "and" are very common and often removed for simple
models. **Stemming** cuts words down to a rough root (playing, played to play), and **lemmatisation** uses a dictionary
to find the proper base form (better to good).

## Bag of words and TF-IDF
The **bag-of-words** model represents a document by counting how often each vocabulary word appears, ignoring word order.
**TF-IDF** improves on raw counts: a word gets a high weight if it is frequent in this document (term frequency) but rare
across the collection (inverse document frequency). Words that appear everywhere get low weights because they do not
help tell documents apart. TF-IDF vectors with a logistic regression classifier are a strong, fast baseline for many
text classification tasks.

## Limits of word counting
Bag-of-words and TF-IDF only match exact words. "car" and "automobile" are treated as completely unrelated, and
"not good" looks almost the same as "good". They also ignore word order and context, so "bank" means the same thing in
"river bank" and "bank loan".

## Word embeddings
Word embeddings such as Word2Vec and GloVe give each word a dense vector learned from large amounts of text, so words used
in similar contexts get similar vectors. This captures meaning much better than counting, but each word still has only
one vector regardless of the sentence it appears in. Contextual models based on transformers solve that problem.

## Evaluating NLP models
Use the same classification metrics as elsewhere (precision, recall, F1), and read some of the mistakes yourself:
sarcasm, negation and spelling errors are common causes.
