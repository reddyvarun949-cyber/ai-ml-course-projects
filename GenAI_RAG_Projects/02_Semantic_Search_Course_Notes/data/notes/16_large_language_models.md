# Large Language Models

Topic: NLP & GenAI

## What an LLM is
A large language model (LLM) is a very large transformer trained to predict the next token of text. After training on a
huge collection of books, websites and code, it can write, summarise, translate, answer questions and generate code,
all from the same basic skill of continuing text.

## How LLMs are trained
Training happens in stages. **Pre-training** teaches next-token prediction on a massive general corpus; this is where the
model picks up grammar, facts and reasoning patterns, and it is extremely expensive. **Instruction tuning** then trains
the model on examples of instructions and good answers so that it follows requests instead of just continuing text.
Finally, methods such as **reinforcement learning from human feedback** use human preference ratings to make answers more
helpful and safer.

## Generating text
The model produces one token at a time. At each step it outputs a probability for every token in its vocabulary and
picks one. **Temperature** controls randomness: a low temperature makes the model choose the most likely tokens and gives
focused, repeatable answers, while a higher temperature gives more varied and creative text. The **context window** is
the maximum number of tokens the model can read and write in one request.

## Hallucinations and other limitations
LLMs can produce fluent text that is simply false, such as invented references or wrong numbers; this is called
**hallucination**. Their knowledge stops at a training cutoff date, they do not know your private documents, and they
can repeat biases found in their training data. Important outputs must be checked by people.

## Using LLMs in applications
Most applications call an LLM through an API: you send messages and receive generated text, paying per token. Open-weight
models can instead be downloaded and run on your own hardware, which helps with privacy but needs a capable GPU. Keep API
keys secret in environment variables and never commit them to code repositories.

## Making answers reliable
Clear prompts, giving the model the relevant documents (retrieval-augmented generation), asking for structured output
such as JSON and validating it, and evaluating answers on a fixed set of test questions all make LLM applications more
dependable.
