# Building Models with Keras

Topic: Deep Learning

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
