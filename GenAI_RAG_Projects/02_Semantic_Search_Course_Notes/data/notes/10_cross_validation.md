# Train, Validation, Test and Cross-Validation

Topic: Machine Learning

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
