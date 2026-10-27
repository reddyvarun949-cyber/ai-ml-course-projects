# Feature Engineering

Topic: Machine Learning

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
