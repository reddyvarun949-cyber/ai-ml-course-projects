# Overfitting and Regularisation

Topic: Machine Learning

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
