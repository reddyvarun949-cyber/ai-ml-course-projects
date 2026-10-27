# Transformers and Attention

Topic: NLP & GenAI

## Why transformers were invented
Older sequence models such as RNNs and LSTMs read text one word at a time. That makes them slow to train and they
struggle to connect words that are far apart in a long passage. The transformer, introduced in the 2017 paper
"Attention Is All You Need", processes all the words of a sequence in parallel and uses attention to connect any word
directly with any other.

## Self-attention in plain words
For each word, self-attention asks: which other words in this sentence should I look at to understand myself? In "The
animal did not cross the street because it was too tired", attention helps the model link "it" to "animal". Technically,
every token produces a **query**, a **key** and a **value** vector. The query of one token is compared with the keys of
all tokens using dot products; a softmax turns these scores into weights; and the output is the weighted average of the
value vectors. The result is a new, context-aware vector for every token.

## Multi-head attention and positions
Several attention "heads" run side by side, each free to focus on a different kind of relationship, for example grammar
in one head and meaning in another. Because attention by itself ignores word order, transformers add **positional
encodings** to the token embeddings so the model knows where each token sits in the sequence.

## Encoders and decoders
The original transformer has an **encoder**, which reads the input, and a **decoder**, which generates output one token at
a time. **BERT** uses only the encoder and is good at understanding tasks such as classification and search. **GPT**
models use only the decoder and are trained to predict the next token, which makes them good at generating text.

## Tokenisation for transformers
Transformers use subword tokenisers. Rare words are split into frequent pieces, so the vocabulary stays manageable while
any word can still be represented. A rough rule for English is that one token is about three quarters of a word.

## Pre-training and fine-tuning
Transformers are first pre-trained on huge amounts of text to learn general language patterns, then fine-tuned on a
smaller labelled dataset for a specific task. This transfer learning is why good results are possible without training
from scratch.
