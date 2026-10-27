# Statistics Basics for Machine Learning

Topic: Statistics

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
