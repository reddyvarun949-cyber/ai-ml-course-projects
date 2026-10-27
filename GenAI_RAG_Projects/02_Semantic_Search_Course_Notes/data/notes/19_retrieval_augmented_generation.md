# Retrieval-Augmented Generation (RAG)

Topic: NLP & GenAI

## The problem RAG solves
A language model only knows what was in its training data. It does not know your company handbook, last week's product
changes or your course notes, and when asked about them it may confidently make something up. Retrieval-augmented
generation fixes this by looking up relevant passages first and giving them to the model together with the question.

## The RAG pipeline
1. **Index:** split your documents into chunks, embed each chunk and store the vectors with their text and source.
2. **Retrieve:** embed the user's question with the same model and find the most similar chunks.
3. **Augment:** build a prompt that contains the question and the retrieved chunks, with instructions such as "Answer only
   from the context below and cite the source".
4. **Generate:** send the prompt to the language model and return its answer with links to the sources.

## Chunking matters
Chunks that are too large mix several topics and waste the context window; chunks that are too small lose the
surrounding explanation. A common starting point is a few hundred words per chunk, split along headings or paragraphs,
with a small overlap so that a sentence cut at the boundary still appears whole in one chunk. Keep metadata such as the
document title and section heading with every chunk.

## Grounding and citations
Tell the model to use only the supplied context and to say "I don't know" when the context does not contain the answer.
Showing the retrieved sources to the user lets them check the answer. If the best retrieval score is low, it is often
better to say that nothing relevant was found than to let the model guess.

## Evaluating a RAG system
Evaluate the two halves separately. **Retrieval quality:** did the right chunk appear in the top results? **Answer
quality:** is the answer correct, complete and supported by the retrieved text? Keep a fixed set of test questions and
re-run it whenever you change chunking, the embedding model or the prompt.

## Common problems
Poor answers usually come from poor retrieval: the right passage was never found. Other causes are chunks without
context, outdated documents in the index and questions that need information spread across many documents. Improvements
include hybrid search (keywords plus embeddings), re-ranking the top results and rewriting the user's question before
searching.
