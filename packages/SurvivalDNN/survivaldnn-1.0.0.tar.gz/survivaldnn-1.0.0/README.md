[![Build](https://img.shields.io/github/actions/workflow/status/adamvvu/survivaldnn/survivaldnn_tests.yml?style=for-the-badge)](https://github.com/adamvvu/survivaldnn/actions/workflows/survivaldnn_tests.yml)
[![PyPi](https://img.shields.io/pypi/v/survivaldnn?style=for-the-badge)](https://pypi.org/project/survivaldnn/)
[![Downloads](https://img.shields.io/pypi/dm/survivaldnn?style=for-the-badge)](https://pypi.org/project/survivaldnn/)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](https://github.com/adamvvu/survivaldnn/blob/master/LICENSE)

Survival Analysis using Deep Learning for Prediction

------------------------------------------------------------------------

## **SurvivalDNN**

[Documentation](https://adamvvu.github.io/survivaldnn/docs/)

SurvivalDNN is a library for survival analysis using deep learning, with a focus on prediction tasks and ease-of-use. Survival analysis models the time until events occur, for example the failure time of industrial components, patient survival times in medicine, customer churn in business, and credit risk in finance. 

### Getting Started

Install from PyPi:
`$ pip install survivaldnn`

#### Usage

1. Specify the model architecture, loss function, and other hyperparameters
```python
from survivaldnn import SurvivalDNNModel

model = SurvivalDNNModel()

# Default: Residual network with negative loglikelihood loss
model.compile(
    numFeatures,
    numSupport=100,
    loss='loglik',
    architecture='resnet',
    layers=3
)
```
2. Train the model
```python
model.fit(X, Y,
          numSupport=100,
          epochs=100)
```
3. Make predictions of interest
```python
# Estimated time until failure
model.predict(X)

# Estimated time until failure, given that `elapsed` time has occurred
model.predict(X, elapsed)

# Estimated full survival function and support
survFunc, support = model.predict_survival_function(X)
```
For a more in-depth example, see this [notebook](https://adamvvu.github.io/survivaldnn/examples/Example.html).

#### Technical Note

*This library builds on and draws from other proposed methodologies such as DeepSurv (Katzman et al., 2018), Nnet-Survival (Gensheimer and Narasimhan, 2018), and DNNSurv (Zhao and Feng, 2021), with a few [modifications](#technical-note) for practical usage, stability during training, and efficiency.*

With discrete-time survival models, the outcome space is discretized into a finite number of support points $\{t_1,\dots, t_k\}$ with $t_{i-1} < t_{i}$ such that\
$$\text{supp}(Y) = \bigcup_{i=1}^{k} (t_{i-1}, t_i]$$\
Deep learning approaches to survival analysis often model the conditional survival probabilities $P(Y > t_j|X, Y > t_{j-1})$, or the probability of surviving each time interval *given* that an individual has survived up to the previous interval. In this library, the outputs of the neural network are instead a $k$-dimensional vector that models the survival function directly:\
$$\Big( P(Y > t_1|X), P(Y > t_2|X), \dots, P(Y > t_k|X) \Big)$$\
which is done by enforcing monotonicity restrictions in the final layer, such that $P(Y > t_{i-1}|X) \geq P(Y > t_i|X)$. The main reasoning for doing so is that for prediction tasks, interest is typically on statistics based on features of $P(Y > t_i|X)$. We can of course still obtain the marginal survival probabilities using the conventional approach with\
$$P(Y > t_j|X) = \prod_{i}^{j} P(Y > t_i|X, Y > t_{i-1})$$\
However this can be numerically unstable and can compound small errors especially when the number of support points is large. By modeling the survival function directly with the additional structure from enforcing monotonicity, this implementation can be more stable during training as well as being more computationally efficient for large-scale prediction tasks.

### References

Gensheimer, M. F., & Narasimhan, B. (2019). A scalable discrete-time survival model for neural networks. PeerJ, 7, e6257. https://doi.org/10.7717/peerj.6257

Katzman, J. L., Shaham, U., Cloninger, A., Bates, J., Jiang, T., & Kluger, Y. (2018). DeepSurv: Personalized treatment recommender system using a Cox proportional hazards deep neural network. BMC Medical Research Methodology, 18(1), 24. https://doi.org/10.1186/s12874-018-0482-1

Zhao, L., & Feng, D. (2020). Deep neural networks for survival analysis using pseudo values. IEEE Journal of Biomedical and Health Informatics, 24(11), 3308–3314. https://doi.org/10.1109/JBHI.2020.2980204