# Linear Regression

Topic: Machine Learning

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
