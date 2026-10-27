# Embeddings and Vector Search

Topic: NLP & GenAI

## Meaning as coordinates
An embedding is a list of numbers, a vector, that represents a piece of text, an image or another item. Embedding models
are trained so that items with similar meaning get vectors that are close together. "How do I reset my password?" and
"I forgot my login details" share almost no words, yet a good embedding model places them near each other.

## How embedding models learn
Modern sentence embedding models are usually trained with a **contrastive** idea: pairs of texts that belong together,
such as a question and its answer, are pulled closer, while unrelated texts are pushed apart. After training on millions
of such pairs, the model maps any new sentence to a point in a space of a few hundred dimensions.

## Measuring similarity
- **Dot product:** multiplies matching coordinates and adds them up.
- **Cosine similarity:** the dot product of the two vectors divided by their lengths; it measures the angle, from -1 to 1,
  and ignores length. It is the most common choice for text.
- **Euclidean distance:** the straight-line distance between two points.
If vectors are normalised to length 1, the dot product and cosine similarity give exactly the same ranking.

## Semantic search
Semantic search finds documents by meaning instead of exact words. The pipeline is: split documents into chunks, embed
each chunk, store the vectors, embed the user's query with the same model, and return the chunks whose vectors are most
similar. Documents and queries must always use the same embedding model; vectors from different models cannot be compared.

## Vector databases
For a few thousand chunks, a NumPy matrix and a brute-force similarity calculation are fast enough. For millions of
vectors, **approximate nearest neighbour** indexes such as HNSW or IVF trade a little accuracy for a large speed-up.
Tools such as FAISS, Chroma, Qdrant, Weaviate, Pinecone and the pgvector extension for PostgreSQL store vectors together
with metadata, so you can filter results, for example by topic or date.

## Evaluating retrieval
Build a small set of test queries with the document that should be found. Measure **hit rate at k** (is the right
document in the top k?), and **mean reciprocal rank** (how high is it, on average?). Look at the failures to decide whether
to change the chunking, the embedding model or the query handling.
