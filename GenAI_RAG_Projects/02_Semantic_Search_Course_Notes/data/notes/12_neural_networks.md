# Neural Networks

Topic: Deep Learning

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
