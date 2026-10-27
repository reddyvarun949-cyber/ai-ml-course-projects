# Data Preprocessing

Topic: Machine Learning

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
