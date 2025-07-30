#########################
# Built-in loss functions
#########################

import tensorflow as tf

@tf.function 
def loglik_loss(y_true, probs_hat):
    """
    Loss function for minimizing negative log-likelihood

    Args:
        y_true     (Tensor)  Encoded array of shape (n, numSupport)
        probs_hat  (Tensor)  Estimated conditional probabilities of shape (n, numSupport)
    """
    eps = tf.constant(1e-4, dtype=tf.float32)
    loss = y_true*tf.math.log(probs_hat + eps) + (1 - y_true)*tf.math.log(1 - probs_hat + eps)
    logLik = tf.math.reduce_sum(loss, axis=-1)
    return -logLik

def get_mse_loss(support):
    """
    Loss function for minimizing MSE of point estimates
    """
    support = tf.expand_dims(tf.constant(support, dtype=tf.float32), axis=-1)    # Shape: (numSupport, 1)

    @tf.function
    def loss(y_true, probs_hat):
        """
        Loss function for minimizing MSE of point estimates

        Args:
            y_true     (Tensor)  Encoded array of shape (n, numSupport)
            probs_hat  (Tensor)  Estimated conditional probabilities of shape (n, numSupport)
        """
        y_true_idx = tf.cast(tf.math.reduce_sum(y_true, axis=-1) - 1., tf.int32)
        y_true_time = tf.gather(support, y_true_idx)
        pointwise_probs = -(probs_hat[:, 1:] - probs_hat[:, :-1])                # Equivalent to -np.diff but missing last element
        bdry = probs_hat[:, -1] * support[-1, :]                                 # Right boundary; Shape: (n,)
        y_hat_time = tf.squeeze(tf.linalg.matmul(pointwise_probs, support[:-1, :]), axis=-1) + bdry   # Point estimate of duration
        mse = tf.math.square(y_true_time - y_hat_time)
        return mse
    return loss

def get_loglik_mse_loss(support):
    """
    Composite loss with maximum likelihood and shrinkage towards MSE
    """
    @tf.function
    def loss(y_true, probs_hat):
        """
        Args:
            y_true     (Tensor)  Encoded array of shape (n, numSupport)
            probs_hat  (Tensor)  Estimated conditional probabilities of shape (n, numSupport)
        """
        # Maximum likelihood estimate
        logLik = loglik_loss(y_true, probs_hat)

        # Shrinkage towards MSE
        mse = get_mse_loss(support)

        # Composite loss
        loss_val = logLik + mse

        return loss_val
    return loss