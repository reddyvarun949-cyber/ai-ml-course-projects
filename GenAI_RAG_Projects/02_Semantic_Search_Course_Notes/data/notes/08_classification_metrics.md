# Classification Metrics

Topic: Machine Learning

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
