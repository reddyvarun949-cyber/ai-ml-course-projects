# Deployment Basics

Topic: Deployment

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
