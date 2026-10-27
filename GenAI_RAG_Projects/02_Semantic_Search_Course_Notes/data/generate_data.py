"""Write the course-notes corpus and the labelled evaluation queries used in this project.

Run from the project root:  python data/generate_data.py

Outputs
    data/notes/*.md          20 short course-note documents (Markdown, one topic each)
    data/eval_queries.csv    labelled search queries: which note SHOULD be found for each query

The notes are original, beginner-level summaries written for this course. Nothing is random here,
so everyone gets exactly the same files (the "seed" is simply the text below).

A little realistic messiness is kept on purpose, because real note collections are never tidy:
    - one note uses '###' sub-headings under its '##' sections,
    - one note has a very long section (so the chunker must split it into several chunks),
    - one note ends with trailing blank lines and spaces,
    - one note has a short "Quick tip" section of only one sentence.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(HERE, "notes")

# Each note: (file name, topic, markdown text). The first line of the text is "# Title".
NOTES = [
    ("01_python_basics.md", "Python & Data", """
# Python Basics for Data Science

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
"""),
    ("02_pandas_dataframes.md", "Python & Data", """
# Working with Tables in pandas

## What a DataFrame is
pandas is the standard Python library for tabular data. A DataFrame is a table with named columns and an index for the
rows, much like a spreadsheet you control with code. Each column is a Series, and every value in a column usually has
the same type. You will use pandas to load, inspect, clean and summarise almost every dataset in this course.

## Loading and inspecting data
Read a CSV file with `df = pd.read_csv("file.csv")`. Then look before you analyse: `df.head()` shows the first rows,
`df.shape` gives the number of rows and columns, `df.info()` lists the column types and how many values are present,
and `df.describe()` summarises the numeric columns with count, mean, standard deviation, minimum and maximum.

## Selecting and filtering
Pick one column with `df["price"]` and several with `df[["price", "city"]]`. Filter rows with a condition:
`df[df["price"] > 100]`. Combine conditions with `&` (and) and `|` (or), putting each condition in brackets. Use
`df.loc[rows, columns]` to select by labels and `df.iloc[rows, columns]` to select by position.

## Missing values and duplicates
Real data has gaps. `df.isna().sum()` counts the missing values in each column. You can drop rows with `dropna`, or
fill gaps with `fillna`, for example with the median. Duplicate rows are found with `df.duplicated()` and removed with
`drop_duplicates`. Always write down how many rows you removed and why, so others can check your work.

## Grouping and aggregating
`groupby` splits the table into groups, applies a calculation to each group and combines the results. For example,
`df.groupby("city")["price"].mean()` gives the average price per city. You can ask for several statistics at once with
`agg`, such as count, mean and maximum. This split-apply-combine pattern answers most "per category" questions.

## Combining tables
`pd.merge(orders, customers, on="customer_id")` joins two tables on a shared key column, like a SQL join. Choose
`how="left"` to keep every row from the first table even when there is no match. `pd.concat` stacks tables on top of
each other when they have the same columns.

## Creating new columns
New columns are often calculated from existing ones: `df["price_per_sqft"] = df["price"] / df["area"]`. Vectorised
operations like this work on the whole column at once and are much faster than looping over rows.
"""),
    ("03_data_visualization.md", "Python & Data", """
# Data Visualization

## Why plot your data
A chart can show in seconds what a table of numbers hides: a skewed distribution, an outlier, a trend over time or
two groups that behave differently. Plotting is part of exploratory data analysis (EDA), the step where you get to
know the data before building any model.

## Choosing the right chart
- **Histogram:** the distribution of one numeric column. Shows skew, gaps and unusual values.
- **Box plot:** compares a numeric column across categories and marks outliers as dots beyond the whiskers.
- **Scatter plot:** the relationship between two numeric columns, for example area and price.
- **Line chart:** how a value changes over time.
- **Bar chart:** counts or averages per category.
- **Heatmap:** a grid of colours, often used to show the correlation between every pair of numeric columns.

## Matplotlib and seaborn
Matplotlib is the base plotting library in Python. You create a figure, draw on its axes and add a title and axis
labels. Seaborn is built on Matplotlib and makes statistical charts with one line, for example
`sns.histplot(df["price"])` or `sns.boxplot(data=df, x="city", y="price")`. Seaborn also adds colour by category with
the `hue` argument.

## Making charts readable
Every chart needs a clear title, labelled axes with units, and a sensible scale. Avoid 3D effects and too many colours.
If labels overlap, rotate them or make the figure wider. Sort bars by value so the reader can compare them quickly.
Use colour to highlight one important group rather than to decorate.

## Reading a chart honestly
Check the axis range before drawing conclusions: a bar chart whose y-axis does not start at zero can make a small
difference look huge. Remember that a pattern in a scatter plot shows correlation, not cause. With very many points,
use transparency (`alpha`) so dense areas are visible.

## Quick tip
Call `plt.tight_layout()` before showing a figure so titles and labels do not overlap.
"""),
    ("04_statistics_basics.md", "Statistics", """
# Statistics Basics for Machine Learning

## Describing data
The **mean** is the average, and the **median** is the middle value when the data is sorted. The median is not pulled
around by extreme values, so it is the better summary for skewed data such as salaries or house prices. The **mode**
is the most frequent value. **Variance** and **standard deviation** measure how spread out the values are around the
mean; a small standard deviation means the values sit close together.

## Distributions
A distribution describes how often each value appears. The **normal distribution** is the symmetric bell curve:
about 68% of values lie within one standard deviation of the mean and about 95% within two. Many real measurements
are not normal; incomes and waiting times are often right-skewed with a long tail of large values.

## Sampling and the central limit theorem
We usually study a sample instead of the whole population. The central limit theorem says that the average of many
random samples follows an approximately normal distribution even when the original data is not normal. This is why
confidence intervals and many statistical tests work in practice.

## Correlation
Correlation measures how strongly two numeric variables move together, from -1 (perfect opposite movement) through
0 (no linear relationship) to +1 (perfect same-direction movement). Correlation does not prove causation: ice-cream
sales and drowning accidents rise together because both increase in hot weather, not because one causes the other.

## Hypothesis testing in plain words
A hypothesis test asks whether a difference we see could easily be due to random chance. We start from the null
hypothesis ("there is no real difference") and compute a **p-value**: the probability of seeing a result at least this
extreme if the null hypothesis were true. A small p-value, commonly below 0.05, suggests the difference is unlikely to
be pure chance. A/B tests on websites use exactly this idea to compare two versions of a page.

## Why this matters for ML
Statistics helps you understand your data before modelling, choose sensible baselines, notice outliers and judge
whether one model is truly better than another or only lucky on one test split.
"""),
    ("05_data_preprocessing.md", "Machine Learning", """
# Data Preprocessing

## Why preprocessing is needed
Most machine learning algorithms need clean numeric input. Raw data contains missing values, text categories, values on
very different scales and mistakes. Preprocessing turns raw data into a form the model can learn from, and it often
matters more for the final result than the choice of algorithm.

## Handling missing values
You can drop rows with missing values when there are only a few, but dropping too many throws information away. The
usual alternative is **imputation**: fill gaps with the median for numeric columns or the most frequent value for
categories. scikit-learn's `SimpleImputer` does this. Sometimes the fact that a value is missing is itself useful, so
you can add a yes/no indicator column.

## Encoding categories
Models cannot multiply the word "Delhi". **One-hot encoding** creates one 0/1 column per category, so "city" becomes
"city_Delhi", "city_Mumbai" and so on. **Ordinal encoding** maps ordered categories such as small < medium < large to
0, 1, 2. Set `handle_unknown="ignore"` on the one-hot encoder so a category that appears only at prediction time does
not crash the model.

## Scaling numeric features
Features measured in very different units, such as age in years and income in rupees, can confuse distance-based models
like k-nearest neighbours and models trained with gradient descent. **Standardisation** (`StandardScaler`) rescales each
column to mean 0 and standard deviation 1. **Min-max scaling** squeezes values into the range 0 to 1. Tree-based models
such as random forests do not need scaling.

## Avoiding data leakage
Leakage happens when information from the test set sneaks into training, which makes results look better than they
will be in real use. The classic mistake is computing the median or the scaler's mean on the full dataset before
splitting. Always split first, then learn preprocessing statistics from the training data only.

## Pipelines
A scikit-learn `Pipeline` chains preprocessing steps and the model into one object. Combined with a `ColumnTransformer`
it applies different steps to numeric and categorical columns. Pipelines prevent leakage during cross-validation and
make deployment simpler, because you save and load one object that does everything.
"""),
    ("06_feature_engineering.md", "Machine Learning", """
# Feature Engineering

## What a feature is
A feature is an input column the model uses to make a prediction. Feature engineering means creating new, more useful
inputs from the raw data using your knowledge of the problem. A good feature can improve a simple model more than
switching to a complex algorithm.

## Creating features from numbers
Ratios and differences often carry the real signal: price per square foot, debt-to-income ratio, or the number of days
between two dates. Binning turns a number into ranges, for example age groups, which can help when the relationship is
not a straight line. A **log transform** compresses large values and makes right-skewed columns such as income easier
for linear models.

## Features from dates and text
A date column can produce the day of the week, the month, whether it is a holiday and how long ago an event happened.
Text columns can produce simple counts (length, number of words) or full vector representations such as TF-IDF, which
you will meet in the NLP notes.

## Interaction features
Sometimes two features matter together: a large house in an expensive area is worth more than the sum of the separate
effects suggests. Multiplying two columns creates an interaction feature. Polynomial features add squares and products
automatically, but they multiply the number of columns quickly, so use them carefully.

## Feature selection
More features are not always better. Irrelevant columns add noise, slow down training and increase the risk that the
model learns accidental patterns. You can remove columns with almost no variation, check which features the model
relies on with permutation importance, or use regularised models that shrink unhelpful weights.

## Domain knowledge first
Talk to people who understand the data. A bank analyst knows which ratios predict loan default; a doctor knows which
lab values belong together. Write down why each engineered feature should help, and then check with validation scores
whether it really does. Never build a feature from information that would not be available at prediction time, such as
a column that is only filled in after the outcome is known.
"""),
    ("07_linear_regression.md", "Machine Learning", """
# Linear Regression

## The idea
Regression predicts a number, such as a house price or tomorrow's temperature. Linear regression assumes the target is
roughly a weighted sum of the inputs plus a constant: price = w1 x area + w2 x bedrooms + b. Training finds the
weights that make the predictions as close as possible to the true values on the training data.

## How the weights are found
The usual goal is to minimise the **mean squared error**: the average of the squared differences between predicted
and actual values. Squaring makes all errors positive and punishes big mistakes more. For linear regression there is a
direct formula for the best weights, but the same goal can also be reached step by step with gradient descent, which is
how neural networks are trained.

## Reading the coefficients
Each weight says how much the prediction changes when that feature increases by one unit and the others stay the same.
A positive weight means the target goes up with the feature. Coefficients are only comparable with each other when the
features are on the same scale, which is another reason to standardise.

## Evaluating a regression model
- **MAE (mean absolute error):** the average size of the error in the target's own units. Easy to explain.
- **RMSE (root mean squared error):** like MAE but larger when there are some big mistakes.
- **R squared:** the share of the variation in the target that the model explains; 1 is perfect and 0 means no better
  than always predicting the average.
Always compare against a baseline that predicts the mean of the training targets.

## Checking assumptions with residuals
A residual is actual minus predicted. Plot residuals against predictions: they should look like random noise around
zero. A curved pattern means the relationship is not linear, and a funnel shape means the errors grow with the size of
the target, which a log transform of the target can often fix.

## When to use something else
If the relationship is strongly non-linear or has many interactions, tree-based models such as random forests or
gradient boosting usually predict better, at the cost of being harder to explain.
"""),
    ("08_classification_metrics.md", "Machine Learning", """
# Classification Metrics

## Why accuracy is not enough
Classification predicts a category, such as spam or not spam. **Accuracy** is the share of correct predictions, but it
can be badly misleading when one class is rare. If only 2% of transactions are fraud, a model that always says "not
fraud" scores 98% accuracy and catches nothing.

## The confusion matrix
A confusion matrix counts four outcomes for a yes/no problem:
- **True positives:** real positives the model found.
- **False positives:** negatives the model wrongly flagged (a false alarm).
- **False negatives:** positives the model missed.
- **True negatives:** negatives correctly left alone.
Every other metric is calculated from these four numbers.

## Precision and recall
**Precision** answers: of everything the model flagged, how much was really positive? **Recall** answers: of all the
real positives, how many did the model catch? A spam filter needs high precision so that important emails are not
hidden. A cancer screening test needs high recall so that sick patients are not missed. The **F1 score** is the
harmonic mean of precision and recall and is useful when you need one number that balances both.

## Thresholds and trade-offs
Most classifiers output a probability. The default rule says "positive if the probability is above 0.5", but you can
move this threshold. A lower threshold catches more positives (higher recall) and raises more false alarms (lower
precision). Choose the threshold based on the real cost of each kind of mistake.

## ROC curve and AUC
The ROC curve plots the true positive rate against the false positive rate for every possible threshold. The area
under it, **ROC AUC**, is the probability that the model ranks a random positive above a random negative: 0.5 is
guessing and 1.0 is perfect. For very imbalanced data the precision-recall curve is often more informative.

## Good practice
Report several metrics, show the confusion matrix, compare with a baseline that always predicts the majority class,
and use a stratified split so that the rare class appears in both training and test sets.
"""),
    ("09_clustering.md", "Machine Learning", """
# Clustering

## Unsupervised learning
In clustering there is no target column. The algorithm groups rows that are similar to each other, and people then
study the groups and give them meaning. Typical uses are customer segmentation, grouping similar documents and finding
unusual records that do not fit any group.

## k-means
k-means needs the number of clusters, k, in advance. It places k centre points, assigns every row to its nearest centre,
moves each centre to the average of its rows, and repeats until the assignments stop changing. Because it uses
distances, features must be scaled first, otherwise the column with the largest numbers dominates. k-means works best
when the groups are roughly round and of similar size.

## Choosing the number of clusters
The **elbow method** plots the within-cluster sum of squares (inertia) for several values of k and looks for the point
where adding clusters stops helping much. The **silhouette score**, from -1 to 1, measures how much closer each point is
to its own cluster than to the next one; higher is better. In business problems, the final choice also depends on how
many groups people can actually act on.

## Other clustering methods
- **Hierarchical (agglomerative) clustering** merges the closest groups step by step and can be drawn as a tree called
  a dendrogram.
- **DBSCAN** finds dense regions of points, does not need k, and labels isolated points as noise. It handles odd
  shapes but is sensitive to its distance setting.

## Interpreting clusters
After clustering, profile each group: compute the average of every feature per cluster and compare it with the overall
average. Give each cluster a short descriptive name only if the profile supports it. Check stability by re-running
with different random seeds; groups that change every run should not drive business decisions.

## Visualising clusters
With many features, reduce them to two dimensions with PCA and colour each point by its cluster. Overlap in the 2D
picture does not always mean overlap in the full space, because the projection loses information.
"""),
    ("10_cross_validation.md", "Machine Learning", """
# Train, Validation, Test and Cross-Validation

## Why we hold data back
A model must be judged on data it did not learn from, because the real goal is to perform well on new cases. We
therefore split the data. The **training set** is used to fit the model, a **validation set** is used to compare models
and choose settings, and a **test set** is kept locked away until the very end to give an honest final estimate.

## The problem with one split
A single random split can be lucky or unlucky: the test rows might happen to be easy or hard. With small datasets the
score can change a lot depending on which rows end up in the test set, so one number can mislead you.

## k-fold cross-validation
Cross-validation splits the training data into k equal folds, often 5. The model is trained k times; each time a
different fold is held out for scoring and the other folds are used for training. You get k scores and report their
mean and standard deviation. The mean is a more reliable estimate, and the standard deviation tells you how stable the
model is.

## Stratified and grouped folds
For classification use **stratified** folds, which keep the class proportions the same in every fold. When several rows
belong to the same person or the same shop, use **grouped** folds so one group never appears in both training and
validation. For time series, always train on the past and validate on the future instead of shuffling.

## Tuning hyperparameters
Hyperparameters are settings you choose before training, such as the depth of a tree or the strength of
regularisation. `GridSearchCV` tries every combination in a grid and scores each one with cross-validation;
`RandomizedSearchCV` tries a random sample of combinations, which is faster when the grid is large. Tune on the training
data only and touch the test set once at the end.

## Common mistakes
Fitting a scaler or imputer on all data before cross-validation leaks information, so put preprocessing inside a
pipeline. Checking the test score many times and changing the model each time slowly turns the test set into a
validation set, and the final score becomes too optimistic.
"""),
    ("11_overfitting_regularisation.md", "Machine Learning", """
# Overfitting and Regularisation

## What overfitting looks like
A model overfits when it learns the training examples too closely, including their noise and accidents, instead of the
general pattern. The sign is a large gap: excellent scores on the training data but much worse scores on validation or
test data. Imagine a student who memorises last year's exam answers word for word and then fails when the questions are
phrased differently.

## Underfitting
The opposite problem is underfitting: the model is too simple to capture the pattern, so it does badly on both training
and test data. A straight line fitted to a clearly curved relationship underfits.

## The bias-variance trade-off
**Bias** is error from overly simple assumptions; **variance** is error from being too sensitive to the particular
training sample. Simple models have high bias and low variance; very flexible models have low bias and high variance.
The aim is the middle ground that generalises best to new data, found by comparing validation scores.

## How to reduce overfitting
- Get more training data, which makes accidental patterns less convincing.
- Use a simpler model or fewer features.
- Limit tree depth or require a minimum number of samples in each leaf.
- Use cross-validation to choose settings honestly.
- For neural networks, use dropout, early stopping and data augmentation.

## Regularisation
Regularisation adds a penalty for complexity to the loss the model minimises, so the model prefers smaller weights.
**L2 regularisation (ridge)** penalises the squared size of the weights and shrinks them all smoothly towards zero.
**L1 regularisation (lasso)** penalises the absolute size of the weights and can push some of them exactly to zero,
which also performs feature selection. Elastic net mixes both. In scikit-learn the strength is controlled by `alpha`
for Ridge and Lasso, and by `C` for logistic regression, where a smaller `C` means stronger regularisation.

Choosing the strength is a balancing act. With almost no penalty the model behaves as if it were not regularised and
can still overfit. With a very strong penalty all weights are squeezed so close to zero that the model ignores useful
features and underfits. Try a range of values, for example 0.01, 0.1, 1, 10 and 100, and keep the one with the best
cross-validated score. Remember to standardise the features first, because the penalty treats all weights the same
way and a feature measured in large units would otherwise be punished unfairly.

### Dropout and early stopping
In neural networks, **dropout** randomly switches off a fraction of neurons during each training step, so the network
cannot rely on any single neuron and must spread what it learns. **Early stopping** watches the validation loss and stops
training when it has not improved for a few epochs, keeping the best weights.

## Learning curves
Plot training and validation scores as the amount of training data grows. If the curves stay far apart, more data or
more regularisation should help; if both are low and close together, the model is underfitting and needs more capacity
or better features.
"""),
    ("12_neural_networks.md", "Deep Learning", """
# Neural Networks

## From a neuron to a network
An artificial neuron takes several inputs, multiplies each by a weight, adds a bias and passes the total through an
activation function. A neural network stacks many neurons into layers: an input layer, one or more hidden layers and an
output layer. Each layer transforms the output of the previous one, which lets the network learn complex, non-linear
patterns.

## Activation functions
Without activation functions a stack of layers would collapse into one linear model. **ReLU** outputs the input if it is
positive and zero otherwise; it is the default for hidden layers because it is simple and trains well. **Sigmoid**
squeezes a value into 0 to 1 and is used for yes/no outputs. **Softmax** turns a list of scores into probabilities that
add up to 1 and is used for multi-class outputs.

## How a network learns
Training repeats four steps. In the **forward pass** the network makes predictions. A **loss function** measures how wrong
they are: mean squared error for numbers, cross-entropy for classes. **Backpropagation** uses the chain rule to work out
how much each weight contributed to the loss. Finally **gradient descent** nudges every weight a small step in the
direction that reduces the loss. The size of that step is the **learning rate**: too large and training jumps around or
diverges, too small and training is very slow.

## Batches and epochs
Instead of using all the data for each update, training uses small **mini-batches**, for example 32 rows. One **epoch**
means the network has seen every training example once. Training usually runs for many epochs while you watch the
training and validation loss.

## Optimisers
Plain stochastic gradient descent uses the same learning rate for every weight. **Adam** adapts the step size for each
weight using running averages of past gradients and is a strong default choice for beginners.

## When neural networks help
Neural networks shine on images, audio and text, where they learn useful features automatically from raw data. For small
tables of numbers, gradient-boosted trees are often just as accurate, faster to train and easier to explain.
"""),
    ("13_keras_tensorflow.md", "Deep Learning", """
# Building Models with Keras

## What Keras is
Keras is the high-level API of TensorFlow for building and training neural networks. You describe the layers, choose a
loss function and an optimiser, and Keras handles the gradient calculations for you. The same few steps work for small
tabular models and for large image or text models.

## The four steps
1. **Define** the model, for example with `keras.Sequential` and a list of `Dense` layers.
2. **Compile** it with an optimiser such as `"adam"`, a loss such as `"sparse_categorical_crossentropy"` and metrics
   such as `"accuracy"`.
3. **Fit** it on training data with `model.fit(X_train, y_train, epochs=20, batch_size=32, validation_split=0.2)`.
4. **Evaluate** it on the test set with `model.evaluate`, then call `model.predict` on new data.

## Reading the training history
`fit` returns a history object with the loss and metrics for every epoch on both training and validation data. Plot
them. If the training loss keeps falling while the validation loss starts rising, the network has begun to memorise
the training set.

## Callbacks
Callbacks run code during training. `EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True)` stops
training when the validation loss stops improving. `ModelCheckpoint` saves the best model to disk while training.

## Common layer types
- `Dense`: every input connects to every neuron; used for tabular data and final outputs.
- `Conv2D` and `MaxPooling2D`: learn local patterns in images.
- `Embedding`: turns word ids into dense vectors for text models.
- `Dropout`: randomly drops neurons during training to reduce overfitting.

## Saving and loading
Save a trained model with `model.save("model.keras")` and load it later with `keras.models.load_model`. Remember to
save any preprocessing too, such as the scaler or the tokenizer vocabulary, because new inputs must be transformed exactly
as the training data was.

## Typical errors
Shape mismatch errors usually mean the input shape does not match the first layer or the labels are in the wrong
format for the loss. Using `sparse_categorical_crossentropy` with one-hot labels, or forgetting to scale pixel values to
0 to 1, are two very common beginner mistakes.
"""),
    ("14_nlp_fundamentals.md", "NLP & GenAI", """
# NLP Fundamentals

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
"""),
    ("15_transformers_attention.md", "NLP & GenAI", """
# Transformers and Attention

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
"""),
    ("16_large_language_models.md", "NLP & GenAI", """
# Large Language Models

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
"""),
    ("17_prompt_engineering.md", "NLP & GenAI", """
# Prompt Engineering

## What a prompt is
A prompt is the input text you give a language model. The same model can give a vague answer or an excellent one
depending on how the request is written. Prompt engineering is the practice of writing clear, specific instructions and
testing them systematically.

## Principles of a good prompt
- **Be specific about the task:** "Summarise this review in two sentences for a product manager" beats "Summarise this".
- **Give context:** who the audience is, what the answer will be used for, and any facts the model needs.
- **Show the format:** ask for bullet points, a table or JSON with named fields.
- **Set boundaries:** say what to do when the information is missing, for example "If the answer is not in the text,
  say you don't know".

## System and user messages
Chat models accept messages with roles. The **system message** sets lasting behaviour, such as "You are a patient tutor
for beginners. Answer in simple English." The **user message** carries the actual request. Keeping rules in the system
message makes behaviour more consistent across a conversation.

## Zero-shot and few-shot prompting
A **zero-shot** prompt simply describes the task. A **few-shot** prompt also includes a handful of worked examples of
input and desired output. Examples are one of the most reliable ways to show the model the style, labels or format you
want, especially for classification and data extraction.

## Asking for step-by-step reasoning
For multi-step problems, asking the model to work through the problem before giving a final answer often improves
accuracy. In applications, ask for the reasoning and the final answer in separate fields so your code can read the answer
reliably.

## Structured output
When code will read the answer, request JSON with exact field names and then validate it. Always handle the case where
the output is not valid JSON, for example by retrying or showing an error.

## Testing prompts
Treat prompts like code. Keep a small set of test inputs, run every prompt version on all of them and compare the results.
Change one thing at a time so you know what helped.

## Prompt injection
If your prompt includes text from users or documents, that text may contain instructions such as "ignore previous
instructions". Clearly separate untrusted content, tell the model to treat it as data, and never give the model more
permissions than the task needs.
"""),
    ("18_embeddings_vector_search.md", "NLP & GenAI", """
# Embeddings and Vector Search

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
"""),
    ("19_retrieval_augmented_generation.md", "NLP & GenAI", """
# Retrieval-Augmented Generation (RAG)

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
"""),
    ("20_deployment_basics.md", "Deployment", """
# Deployment Basics

## What deployment means
A model in a notebook helps nobody else. Deployment means making the model available to users or other programs,
reliably and repeatedly. The most common pattern for beginners is a **web API**: a small server that receives input as
JSON, runs the model and returns the prediction as JSON.

## Save once, load once
Train the model in a notebook or script and save it to a file, for example with `joblib.dump` for scikit-learn pipelines
or `model.save` for Keras. The API loads the file once when it starts and reuses it for every request. Never retrain the
model inside a request; it is slow and gives inconsistent results.

## Building an API with Flask
Flask maps URLs to Python functions. A typical project has a health endpoint that reports whether the model is loaded,
and a prediction endpoint that accepts a POST request with JSON. The prediction function should validate every input
field, return clear error messages with a 4xx status code when something is wrong, and only then call the model.

## Talking to a frontend
A web page built with React or plain HTML sends requests to the API with `fetch`. Because the page and the API run on
different ports, the browser applies **CORS** rules, and the API must send a header allowing the page's origin. Show a
loading state while waiting and a friendly message when the API cannot be reached.

## Environments and dependencies
List the packages and versions your project needs in `requirements.txt` and install them in a virtual environment.
Keep secrets such as API keys in environment variables, not in the code. **Docker** packages the code, the libraries and
the model into one image that runs the same way on any machine.

## Testing and monitoring
Write automated tests for the API: a valid request, each kind of invalid input and the health check. After release,
log requests, response times and errors. Watch for **data drift**: when real inputs start to look different from the
training data, the model's accuracy can drop silently and it may need retraining.

## Going to production
For real traffic, run Flask behind a production server such as gunicorn, add authentication and rate limiting, and
version your models so you can roll back if a new one performs worse.
"""),
]

# Evaluation queries: (query, expected note file, query_type)
#   paraphrase  - asked in different words, but shares a few key words with the note
#   no_overlap  - written to share (almost) no important words with the note: needs "meaning", not keywords
#   off_topic   - not covered by the notes at all: the right answer is "no good match" (expected_doc = none)
EVAL_QUERIES = [
    ("how do I stop my model memorising the training data", "11_overfitting_regularisation.md", "paraphrase"),
    ("my model is great on the data it learned from but terrible on new examples", "11_overfitting_regularisation.md", "no_overlap"),
    ("penalty that shrinks the weights of a linear model", "11_overfitting_regularisation.md", "paraphrase"),
    ("fill in the blanks in a spreadsheet column before training", "05_data_preprocessing.md", "no_overlap"),
    ("turn city names into numbers for a model", "05_data_preprocessing.md", "paraphrase"),
    ("the model looks 98 percent right but never catches the rare cases", "08_classification_metrics.md", "no_overlap"),
    ("difference between precision and recall", "08_classification_metrics.md", "paraphrase"),
    ("how many groups should k-means use", "09_clustering.md", "paraphrase"),
    ("split shoppers into groups that behave alike without labels", "09_clustering.md", "no_overlap"),
    ("average the score over several different train and test splits", "10_cross_validation.md", "paraphrase"),
    ("find the best settings for a model before training", "10_cross_validation.md", "paraphrase"),
    ("draw a picture to compare categories and spot strange values", "03_data_visualization.md", "no_overlap"),
    ("which chart shows the spread of one number column", "03_data_visualization.md", "paraphrase"),
    ("join two tables on a shared id", "02_pandas_dataframes.md", "paraphrase"),
    ("average price for every city in my table", "02_pandas_dataframes.md", "paraphrase"),
    ("does a link between two things prove one causes the other", "04_statistics_basics.md", "paraphrase"),
    ("is the gap between version A and version B of my website real or luck", "04_statistics_basics.md", "no_overlap"),
    ("make new input columns from dates and ratios", "06_feature_engineering.md", "paraphrase"),
    ("predict a number like the price of a flat with a weighted sum", "07_linear_regression.md", "paraphrase"),
    ("how a network adjusts itself after each wrong guess", "12_neural_networks.md", "no_overlap"),
    ("what does the learning rate do", "12_neural_networks.md", "paraphrase"),
    ("stop training automatically when validation loss stops improving in keras", "13_keras_tensorflow.md", "paraphrase"),
    ("count words in documents and give rare words more weight", "14_nlp_fundamentals.md", "paraphrase"),
    ("how does a model know which earlier words matter for the current word", "15_transformers_attention.md", "no_overlap"),
    ("why does the chatbot confidently invent facts that are not true", "16_large_language_models.md", "no_overlap"),
    ("give the model a few worked examples inside the request", "17_prompt_engineering.md", "paraphrase"),
    ("find text with similar meaning even when different words are used", "18_embeddings_vector_search.md", "paraphrase"),
    ("let a chatbot answer questions about my own private documents", "19_retrieval_augmented_generation.md", "no_overlap"),
    ("put my trained model online so a web page can use it", "20_deployment_basics.md", "no_overlap"),
    ("convert a value from text to an integer in python", "01_python_basics.md", "paraphrase"),
    ("best recipe for chicken biryani", "none", "off_topic"),
    ("who won the football world cup", "none", "off_topic"),
    ("cheapest flights from mumbai to goa", "none", "off_topic"),
    ("how do I train my puppy to sit", "none", "off_topic"),
    ("where do pythons live in the wild", "none", "off_topic"),
]


def write_notes():
    os.makedirs(NOTES_DIR, exist_ok=True)
    for name, topic, text in NOTES:
        body = text.strip("\n")
        lines = body.split("\n")
        # line 1 = "# Title", line 2 = topic tag, then the content
        out = lines[0] + "\n\nTopic: " + topic + "\n" + "\n".join(lines[1:]) + "\n"
        if name == "09_clustering.md":
            out += "\n   \n\n"   # messy ending on purpose (trailing blank lines and spaces)
        with open(os.path.join(NOTES_DIR, name), "w", encoding="utf-8") as f:
            f.write(out)
    return len(NOTES)


def write_queries():
    names = {n for n, _, _ in NOTES}
    path = os.path.join(HERE, "eval_queries.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["query_id", "query", "expected_doc", "query_type"])
        for i, (q, doc, kind) in enumerate(EVAL_QUERIES, start=1):
            assert doc == "none" or doc in names, doc
            w.writerow([i, q, doc, kind])
    return len(EVAL_QUERIES)


if __name__ == "__main__":
    n_notes = write_notes()
    n_q = write_queries()
    words = [len(t.split()) for _, _, t in NOTES]
    print(f"Wrote {n_notes} notes to {NOTES_DIR} ({min(words)}-{max(words)} words each)")
    print(f"Wrote {n_q} evaluation queries to {os.path.join(HERE, 'eval_queries.csv')}")
