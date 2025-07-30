from survivaldnn import SurvivalDNNModel
import numpy as np
import pandas as pd
np.random.seed(42)
import pytest

def generate_synthetic_data(n=100):
    
    # Observed features
    length = np.random.uniform(1., 8., size=n)
    width = np.random.uniform(0.5, 4., size=n)
    widget_factor = np.random.uniform(0.2, 2., size=n)
    X = np.stack([length, width, widget_factor], axis=-1)

    # True DGP (Unobserved)
    epsilon = np.random.normal(0, 0.1,size=n)
    U = 2 - 0.1*length - 0.1*width - widget_factor + epsilon
    rate = np.exp(U)

    # Observed outcomes
    Y = np.random.exponential(scale=1/rate)
    
    return X, Y
    
def _test_discretize(Y, numSupport=5):
    model = SurvivalDNNModel()
    assert len(model.discretize_outcome_support(Y, numSupport=numSupport)) == numSupport, 'Incorrect number of support points'

def _test_compile(model, numFeatures=3, numSupport=5):
    model = SurvivalDNNModel()

    # Test default compilation
    model.compile(
        numFeatures=numFeatures, 
        numSupport=numSupport,
    )

    # Test with custom architecture
    model.compile(
        numFeatures=numFeatures, 
        numSupport=numSupport,
        architecture=[32,32],
    )

    # Test with dropout
    model.compile(
        numFeatures=numFeatures, 
        numSupport=numSupport,
        dropout=0.2
    )

    # Test without batchnorm
    model.compile(
        numFeatures=numFeatures, 
        numSupport=numSupport,
        batchnorm=False
    )

def _test_train(X, Y, model):
    model.fit(X, Y,
          epochs=2)
    
def _test_predict(X, model):
    Y_hat = model.predict(X)
    assert len(Y_hat) == X.shape[0], 'Prediction shape mismatch'

def _test_predict_conditional(X, model):
    Y_hat = model.predict_conditional(X, elapsed=np.ones(X.shape[0]))
    assert len(Y_hat) == X.shape[0], 'Conditional prediction shape mismatch'

def _test_predict_survival(X, model):
    survFunc, support = model.predict_survival_function(X)
    assert survFunc.shape == (X.shape[0], model.numSupport), 'Survival function shape mismatch'
    assert len(support) == model.numSupport, 'Support shape mismatch'

def test_RunAllTests():

    X, Y = generate_synthetic_data(100)
    numSupport = 5

    _test_discretize(Y, numSupport)

    model = SurvivalDNNModel()
    _test_compile(model, numFeatures=X.shape[-1], numSupport=numSupport)

    model = SurvivalDNNModel()
    model.compile(numFeatures=X.shape[-1], numSupport=numSupport)
    _test_train(X, Y, model=model)
    _test_predict(X, model)
    _test_predict_conditional(X, model)
    _test_predict_survival(X, model)

    return