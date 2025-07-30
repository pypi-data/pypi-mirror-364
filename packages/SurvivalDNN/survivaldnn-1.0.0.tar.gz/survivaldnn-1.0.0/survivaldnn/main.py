from survivaldnn.losses import *

from typing import Union, Optional, Callable
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import tensorflow as tf
import tensorflow.keras as tfk
from tf_compactprogbar import CompactProgressBar

class SurvivalDNNModel(tf.Module):
    """
    Random Survival DNN model for modeling the distribution of time-to-events
    """
    def __init__(self, dtype : tf.dtypes.DType=tf.float32):
        self.dtype = dtype
        
        self.modelName = 'SurvivalModel'
        self.model = None
        self.support = None
        self.numSupport = None
        self.optimizer = None
        self.loss_fn = None
        self.delayModelCompile = False
        self.isCompiled = False

    def compile(self, 
                numFeatures : int, 
                numSupport : int,
                loss : Union[str, Callable[[tf.Tensor, tf.Tensor], tf.Tensor]]='loglik',
                architecture : Union[str, list]='resnet', 
                layers : int=3, 
                activation : tfk.layers=tfk.layers.LeakyReLU,
                batchnorm : bool=True,
                dropout : float=0., 
                l2 : float=0., 
                optimizer : Optional[tfk.optimizers.Optimizer]='adam',
                lr : Optional[tfk.optimizers.schedules.LearningRateSchedule]=0.001):
        """
        Compiles the Survival DNN model

        Args:
            numFeatures     (int)          Dimensionality of features
            numSupport      (int)          Dimensionality of discretized outcome space
            loss            (str, func)    Built-in loss function or a TensorFlow callable
            architecture    (str, list)    Architecture. See note.
            layers          (int)          Number of fixed-width hidden layers. Ignored if `architecture` != 'resnet'
            activation      (obj)          Activation function for hidden layers
            batchnorm       (bool)         Whether to use batch normalization between each hidden layer
            dropout         (float)        Dropout rate
            l2              (float)        L2 regularization penalty on weights
            optimizer       (str, obj)     TensorFlow Keras Optimizer

        Notes: 
            The `architecture` of the model defaults to a fixed-width DNN with residual connections,
            with `layers` number of hidden layers. Either the number of hidden layers must be specified,
            or an explicit architecture, e.g. [32, 32]

            Built-in loss functions include: 
                - 'loglik'       Negative loglikelihood 
                - 'mse'          MSE of point estimates of E[Y|X] 
                - 'loglik_mse'   Composite loss of loglikelihood with shrinkage towards MSE
        """
        # Parse configuration and user settings
        if architecture == 'resnet':
            resnet = True
            numLayers = layers
            layerNodes = [numFeatures for _ in range(numLayers)]
        else:
            resnet = False
            numLayers = len(architecture)
            layerNodes = architecture
        if loss == 'loglik':
            self.loss_fn = loglik_loss
        elif loss == 'mse':
            self.delayModelCompile = True
            self.loss_fn = get_mse_loss
        elif loss == 'loglik_mse':
            self.delayModelCompile = True
            self.loss_fn = get_loglik_mse_loss
        elif callable(loss):
            self.loss_fn = loss
        else:
            raise Exception('Invalid loss function. Must be in ["loglik", "mse", "loglik_mse"] or a callable function')
        self.dropout = dropout
        self.batchnorm = batchnorm
        self.numSupport = numSupport

        ## Model Architecture

        # Input: Features
        featureLayer = tfk.layers.Input(shape=(numFeatures,))
        f0 = featureLayer
        
        # Hidden layers
        f = f0
        for i, nodes in enumerate(layerNodes):
            lastLayer = False
            if i == (numLayers-1): 
                lastLayer = True
    
            # Feedforward connections
            f = self._create_dense_layer(nodes, l2=l2)(f)
            if batchnorm:
                f = tfk.layers.BatchNormalization(axis=-1)(f)
            f = activation()(f)

            # Optional Dropout/Residual connections
            if (not lastLayer) and (dropout > 0):
                f = tfk.layers.Dropout(dropout)(f)
            if resnet:
                f = tfk.layers.Add()([f, f0])
            f = activation()(f)
    
        # Pooling layer
        f = self._create_dense_layer(
                    self.numSupport,
                    kernel_initializer=tfk.initializers.RandomNormal(0, 0.01)
                )(f)

        # Output: Conditional probabilities of survival P(T >= t|X)
        probs = MonotoneProbabilities(dtype=self.dtype)(f)
        self.model = tfk.Model(inputs=featureLayer, outputs=probs, name='SurvivalModel')

        ## Compile model
        if optimizer == 'adam':
            self.optimizer = tfk.optimizers.Adam(learning_rate=lr, clipnorm=1)
        if not self.delayModelCompile:
            self._compile_model(
                optimizer=self.optimizer, 
                loss_fn=self.loss_fn
            )
        self.isCompiled = True

    def fit(self, X : Union[np.ndarray, pd.DataFrame], 
                  Y : Union[np.ndarray, pd.DataFrame],
                  val_data : Optional[tuple]=None, 
                  epochs : int=5000, 
                  batch_size : int=10000, 
                  tboard : bool=False, 
                  tboard_suffix : str=''):
        """
        Trains the model

        Args:
            X              (array-like)    Features of shape (n, num_features)
            Y              (array-like)    Outcomes/durations of shape (n,1) or (n,)
            val_data       (tuple)         Validation data: (val_X, val_Y)
            epochs         (int)           Number of training epochs
            batch_size     (int)           Batch size
            tboard         (bool)          Whether to profile with TensorBoard
            tboard_suffix  (str)           Suffix on TensorBoard profile filenames

        Outcomes should be an array of the duration/survival times for each individual. By default, the outcome space is discretized and
        encoded into `support_bins` number of bins. Pass `None` to use all unique values as the support, e.g. for integer-valued outcomes.
        """
        self._check_compiled()
        
        # Process data
        X, Y = self._process_features(X), self._process_outcomes(Y)
        hasVal = False
        if val_data is not None:
            X_val, Y_val = val_data
            X_val, Y_val = self._process_features(X_val), self._process_outcomes(Y_val)
            hasVal = True

        # Support of modeled distribution
        ## Bins: (t0, t1], (t1, t2], ..., (t_{k-1}, t-k]
        ##  where t_k = max(Y), t_0 = min(Y)
        if self.support is None:
            if hasVal:
                Y_full = np.concatenate([Y, Y_val])
            else:
                Y_full = Y
            self.support = self.discretize_outcome_support(Y_full, self.numSupport)

        # Delayed compilation if necessary
        if self.delayModelCompile:
            self._compile_model(
                optimizer=self.optimizer,
                loss_fn=self.loss_fn(self.support)
            )
            self.delayModelCompile = False
        
        # Encode outcomes
        Y = self._encode_outcomes(Y)
        if hasVal:
            Y_val = self._encode_outcomes(Y_val)
            val_data = (X_val, Y_val)

        # Train model
        history = self.model.fit(X, Y,
                      batch_size=batch_size,
                      epochs=epochs,
                      verbose=0,
                      shuffle=True,
                      validation_data=val_data,
                      callbacks=self._get_callbacks(
                                    hasVal=hasVal, 
                                    tboard=tboard, 
                                    tboard_suffix=tboard_suffix,
                                )
                    )
        self.history = history.history
        
        # Post-training: Update batch norm statistics without dropout (Hendrycks and Gimpel, 2017)
        if self.batchnorm and self.dropout > 0:
            self._toggle_dropout(True)
            for idx in range(0, len(X), batch_size):
                X_batch = tf.constant(X[idx:(idx+batch_size), :], dtype=self.dtype)
                self.model(X_batch, training=True)
            self._toggle_dropout(False)
     
    def predict_survival_function(self, X, batch_size=2000) -> tuple[np.ndarray, np.ndarray]:
        """
        Predicts the full survival function S(t|X) = P(T >= t|X)

        Returns:
            survFunc  (np.array)  Evaluation of survival function on support, shape (n, numSupport)
            support   (np.array)  Support points of t, shape (numSupport)
        """
        self._check_compiled()
        X = self._process_features(X)
        
        N = len(X)
        survFunc = []
        for idx in range(0, N, batch_size):
            
            # Estimates of conditional probabilities P(T >= t | X)
            X_batch = tf.constant(X[idx:(idx+batch_size), :], dtype=self.dtype)
            condProbs = self.model(X_batch, training=False).numpy()
            
            # Estimates of survival function
            survFunc.append(condProbs)
        survFunc = np.concatenate(survFunc, axis=0)
        support = self._get_support()
        return survFunc, support
    
    def predict(self, X, method='right', batch_size=2000) -> np.ndarray:
        """
        Estimate the expected time-to-event, E[Y|X]

        Args:
            X           (array-like)    Features of shape (n, numFeatures)
            method      (str)           Integration by 'midpoint' or 'right'
            batch_size  (int)           Batch size
        """
        self._check_compiled()
        X = self._process_features(X)
        N = len(X)
        support = self._get_support(method=method)
        Y_hat = []
        for idx in range(0, N, batch_size):
            X_batch = X[idx:(idx+batch_size), :]
        
            # Estimated survival function: P(T >= t| X)
            survFunc, _ = self.predict_survival_function(X_batch, batch_size=batch_size)
    
            # Estimated PMF: P(T = t|X)
            probs = -np.diff(survFunc, append=0)
    
            # Expected time-to-event
            Y_hat_batch = probs @ support
            Y_hat.extend(list(Y_hat_batch))
        return np.ravel(np.array(Y_hat))

    def predict_conditional(self, X, elapsed, method='right', batch_size=2000):
        """
        Estimate the expected time-to-event conditional on elapsed, E[Y|X, Y >= elapsed]

        Args:
            X           (array-like)    Features of shape (n, numFeatures)
            elapsed     (array-like)    Array of shape (n,) indicating elapsed times
            method      (str)           Integration by 'midpoint' or 'right'
            batch_size  (int)           Batch size
        """
        self._check_compiled()
        X, elapsed = self._process_features(X), self._process_outcomes(elapsed)
        if len(X) != len(elapsed):
            raise Exception(f'Mismatched shapes. Received {len(X)} features and {len(elapsed)} times.')
        support = self._get_support(method=method)
        Y_hat = []
        N = len(X)
        for idx in range(0, N, batch_size):
            X_batch = X[idx:(idx+batch_size), :]
            elapsed_batch = elapsed[idx:(idx+batch_size)]
        
            # Estimated survival function: P(T >= t|X)
            survFunc, _ = self.predict_survival_function(X_batch, batch_size=batch_size)
    
            # Estimated PMF: P(T = t|X)
            probs = -np.diff(survFunc, append=0)

            # Zero-indexed indicator for support bins
            elapsed_idx = np.minimum(np.digitize(elapsed_batch, support, right=True), len(support))

            # Expected conditional time-to-event
            Y_hat_batch = []
            for i, bin_idx in enumerate(elapsed_idx):
                truncated_probs = probs[i, bin_idx:]
                truncated_support = support[bin_idx:]
                y = (truncated_probs @ truncated_support) / (np.sum(truncated_probs) + 1e-6)
                Y_hat_batch.append(y)
            Y_hat.extend(list(Y_hat_batch))
        return np.ravel(np.array(Y_hat))

    def plot_survival_function(self, X, batch_size=100):
        """
        Plots the survival function
        """
        survFunc, support = self.predict_survival_function(X, batch_size=batch_size)
        for n, s in enumerate(survFunc):
            plt.step(support, s, where="post", label=str(n))
        plt.ylabel("Survival Probability")
        plt.xlabel("Time")
        plt.legend('')
        plt.show()

    def plot_distribution(self, X, batch_size=100):
        """
        Plots the CDF P(T<=t|X)
        """
        survFunc, support = self.predict_survival_function(X, batch_size=batch_size)
        F = 1 - survFunc
        for n, Fn in enumerate(F):
            plt.step(support, Fn, where="post", label=str(n))
        plt.ylabel("CDF")
        plt.xlabel("Time")
        plt.legend('')
        plt.show()

    def discretize_outcome_support(self, Y : Union[np.array, pd.DataFrame], numSupport : int=100):
        """
        Gets the discretized support of the outcome space

        Args:
            Y               (array-like)    Outcome durations of interest
            numSupport      (int)           Number of support bins. Pass `None` to use all unique integer values as support    
        """
        if numSupport is None:
            bins = np.sort(np.unique(np.round(Y)))
        else:
            _, bins = pd.qcut(Y, numSupport-1, retbins=True)   # Note: These are left-open endpoints, (t0, t1], (t1, t2], ...
        return bins

    def _create_dense_layer(self, nodes, kernel_initializer='he_normal', l2 : float=0., name=None):
        """
        Standard fully-connected layer
        """
        regularizer = None
        if l2 > 0:
            regularizer = tfk.regularizers.L2(l2)
        layer = tfk.layers.Dense(nodes,
                             kernel_initializer=kernel_initializer,
                             kernel_regularizer=regularizer,
                             bias_initializer=tfk.initializers.RandomNormal(0, 1e-4),
                             name=name
                            )
        return layer

    def _compile_model(self, optimizer, loss_fn):
        self.model.compile(
                optimizer=optimizer,
                loss=loss_fn
            )
        self.isCompiled = True

    def _process_outcomes(self, Y):
        """
        Discretizes and flattens outcomes
        Args:
            - Y  (array-like)  DataFrame/Array with a single column of shape (n,1) or (n,)
        """
        if isinstance(Y, pd.DataFrame):
            Y = Y.values
        Y = np.ravel(Y)
        return self._tensor(Y)

    def _encode_outcomes(self, Y):
        """
        Encodes outcomes in discrete-time bins for survival/failure
        Ex.
         Y = [3,1,2] ->  support = [1,2,3]
                         Y_enc = [[1,1,1],[1,0,0,],[1,1,0]]
        Returns:
            Y_encoded (np.array) of shape (n, numSupport)
        """
        Y = np.ravel(Y)
        
        # Zero-indexed indicator for support bins
        Y_idx = np.minimum(np.digitize(Y, self.support, right=True), len(self.support))

        # Encoded arrays for survival
        Y_enc = np.zeros((len(Y), len(self.support)))
        mask = (np.arange(len(self.support)) <= Y_idx[:, None])
        Y_enc[mask] = 1

        return Y_enc
        
    def _process_features(self, X):
        if isinstance(X, pd.DataFrame):
            X = X.values
        return self._tensor(X)
    
    def _tensor(self, z):
        return tf.cast(z, self.dtype)

    def _check_compiled(self):
        if not self.isCompiled:
            raise Exception('Model must be compiled first!')

    def _get_callbacks(self, hasVal=True, tboard=False, tboard_suffix='', min_delta=1e-6):  
        """
        Returns a list of callbacks for training
        """
        callbacks = [CompactProgressBar(exclude=['lr']),]
        if hasVal:
            callbacks += [
                tfk.callbacks.EarlyStopping(min_delta=min_delta, mode='min', patience=50, restore_best_weights=True),
                tfk.callbacks.ReduceLROnPlateau(min_delta=min_delta, mode='min', factor=0.5, patience=20),
            ]
        if tboard:
            currTime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            log_dir = 'logs/' + f'{currTime}_{self.modelName}_{tboard_suffix}'
            callbacks += [
                tfk.callbacks.TensorBoard(log_dir=log_dir, write_graph=False, histogram_freq=1),
            ]

        return callbacks

    def _toggle_dropout(self, mode : bool=True):
        """
        Toggles dropout layers on and off
        """
        self._check_compiled()
        for layer in self.model.layers:
            if isinstance(layer, tfk.layers.Dropout):
                if mode:
                    rate = float(self.dropout)
                else:
                    rate = 0.
                layer.rate = rate

    def _get_support(self, method='right'):
        """
        Returns the support of the modeled distribution for T 
        """
        self._check_compiled()
        if method=='right':
            support = self.support
        elif method=='midpoint':
            support = (self.support[:-1] + self.support[1:]) / 2
        return support

class MonotoneProbabilities(tfk.layers.Layer):
    """
    Output layer that enforces monotonically decreasing shape restrictions as probabilities
    """
    def __init__(self, dtype : tf.dtypes.DType=tf.float32, **kwargs):
        super(MonotoneProbabilities, self).__init__(**kwargs)
        self.epsilon = tf.constant(1e-6, dtype=dtype)
    
    def call(self, x):
        """
        Inputs to layer should be all of R
        """
        # Monotonicity transformation
        x = tf.math.square(x)               # Larger |x| -> Smaller prob.
        x = tf.math.cumsum(x, axis=-1)
        x = tf.math.exp(-x)
        return x

