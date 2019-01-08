"""
Implementing Different Layers
We will illustrate how to use different types of layers in TensorFlow
The layers of interest are:
 (1) Convolutional Layer
 (2) Activation Layer
 (3) Max-Pool Layer
 (4) Fully Connected Layer
We will generate two different data sets for this
 script, a 1-D data set (row of data) and
 a 2-D data set (similar to picture)
"""

import tensorflow as tf
import numpy as np
from tensorflow.python.framework import ops
ops.reset_default_graph()

# ---------------------------------------------------|
# -------------------1D-data-------------------------|
# ---------------------------------------------------|

# Create graph session
sess = tf.Session()

# parameters for the run
data_size = 25
conv_size = 5
maxpool_size = 5
stride_size = 1

# ensure reproducibility
seed = 13
np.random.seed(seed)
tf.set_random_seed(seed)

# Generate 1D data
data_1d = np.random.normal(size=data_size)

# Placeholder
x_input_1d = tf.placeholder(dtype=tf.float32, shape=[data_size])


# --------Convolution--------
def conv_layer_1d(input_1d, input_filter, stride):
    """
    TensorFlow's 'conv2d()' function only works with 4D arrays:
    [batch#, width, height, channels], we have 1 batch, and
    width = 1, but height = the length of the input, and 1 channel.
    So next we create the 4D array by inserting dimension 1's.
    :param input_1d: 1D input array.
    :param input_filter: Filter to convolve across the input_1d array.
    :param stride: stride for filter.
    :return: array.
    """
    input_2d = tf.expand_dims(input_1d, 0)
    input_3d = tf.expand_dims(input_2d, 0)
    input_4d = tf.expand_dims(input_3d, 3)
    # Perform convolution with stride = 1, if we wanted to increase the stride,
    # to say '2', then strides=[1,1,2,1]
    convolution_output = tf.nn.conv2d(input_4d,
                                      filter=input_filter,
                                      strides=[1, 1, stride, 1],
                                      padding="VALID")
    # Get rid of extra dimensions
    conv_output_1d = tf.squeeze(convolution_output)
    return conv_output_1d

# Create filter for convolution.
# note:
# shape of input = [batch, in_height, in_width, in_channels]
# shape of filter = [filter_height, filter_width, in_channels, out_channels]
# Notice that in the input, the width is on the 3rd slot but in the filter, 
# the width is on the 2nd slot
my_filter = tf.Variable(tf.random_normal(shape=[1, conv_size, 1, 1]))
# Create convolution layer
my_convolution_output = conv_layer_1d(x_input_1d, my_filter, stride=stride_size)


# --------Activation--------
def activation(input_1d):
    return tf.nn.relu(input_1d)

# Create activation layer
my_activation_output = activation(my_convolution_output)


# --------Max Pool--------
def max_pool(input_1d, width, stride):
    """
    Just like 'conv2d()' above, max_pool() works with 4D arrays.
    [batch_size=1, width=1, height=num_input, channels=1]
    :param input_1d: Input array to perform max-pool on.
    :param width: Width of 1d-window for max-pool
    :param stride: Stride of window across input array
    :return: max-pooled array
    """
    input_2d = tf.expand_dims(input_1d, 0)
    input_3d = tf.expand_dims(input_2d, 0)
    input_4d = tf.expand_dims(input_3d, 3)
    # Perform the max pooling with strides = [1,1,1,1]
    # If we wanted to increase the stride on our data dimension, say by
    # a factor of '2', we put strides = [1, 1, 2, 1]
    # We will also need to specify the width of the max-window ('width')
    pool_output = tf.nn.max_pool(input_4d, ksize=[1, 1, width, 1],
                                 strides=[1, 1, stride, 1],
                                 padding='VALID')
    # Get rid of extra dimensions
    pool_output_1d = tf.squeeze(pool_output)
    return pool_output_1d

my_maxpool_output = max_pool(my_activation_output, width=maxpool_size, stride=stride_size)


# --------Fully Connected--------
def fully_connected(input_layer, num_outputs):
    # First we find the needed shape of the multiplication weight matrix:
    # The dimension will be (length of input) by (num_outputs)
    weight_shape = tf.squeeze(tf.stack([tf.shape(input_layer), [num_outputs]]))
    # Initialize such weight
    weight = tf.random_normal(weight_shape, stddev=0.1)
    # Initialize the bias
    bias = tf.random_normal(shape=[num_outputs])
    # Make the 1D input array into a 2D array for matrix multiplication
    input_layer_2d = tf.expand_dims(input_layer, 0)
    # Perform the matrix multiplication and add the bias
    full_output = tf.add(tf.matmul(input_layer_2d, weight), bias)
    # Get rid of extra dimensions
    full_output_1d = tf.squeeze(full_output)
    return full_output_1d

my_full_output = fully_connected(my_maxpool_output, 5)

def check_tensor(input_layer, num_outputs):
    #return tf.shape(input_layer) # gives [17]
    #return tf.stack([tf.shape(input_layer), [num_outputs]]) # gives [[17]
                                                            #        [ 5]]
                                                            
    #return tf.squeeze(tf.stack([tf.shape(input_layer), [num_outputs]])) # gives [17 5]
    return tf.expand_dims(input_layer, 0) # return [input_layer] instead of input_layer
    
check = check_tensor(my_maxpool_output, 5)

# Initialize Variables
init = tf.global_variables_initializer()
sess.run(init)

feed_dict = {x_input_1d: data_1d}

print('>>>> 1D Data <<<<')

# Convolution Output
print('Input = array of length {}'.format(x_input_1d.shape.as_list()[0]))
print('Convolution w/ filter, length = {}, stride size = {},'
      'results in an array of length {}:'.format(conv_size,
                                                 stride_size,
                                                 my_convolution_output.shape.as_list()[0]))
print(sess.run(my_convolution_output, feed_dict=feed_dict))

# Activation Output
print('\nInput = above array of length {}'.format(my_convolution_output.shape.as_list()[0]))
print('ReLU element wise returns '
      'an array of length {}:'.format(my_activation_output.shape.as_list()[0]))
print(sess.run(my_activation_output, feed_dict=feed_dict))

# Max Pool Output
print('\nInput = above array of length {}'.format(my_activation_output.shape.as_list()[0]))
print('MaxPool, window length = {}, stride size = {},'
      'results in the array of length {}'.format(maxpool_size,
                                                 stride_size,
                                                 my_maxpool_output.shape.as_list()[0]))
print(sess.run(my_maxpool_output, feed_dict=feed_dict))

# Fully Connected Output
print('\nInput = above array of length {}'.format(my_maxpool_output.shape.as_list()[0]))
print('Fully connected layer on all 4 rows '
      'with {} outputs:'.format(my_full_output.shape.as_list()[0]))
print(sess.run(my_full_output, feed_dict=feed_dict))


#print('Check = ')
#print(sess.run(check, feed_dict=feed_dict))


# ===================
# 2D data
# ===================
ops.reset_default_graph()
sess=tf.Session()

# Parameters for the run 
row_size = 10 
col_size = 10 
conv_size = 2 
conv_stride_size = 2 
maxpool_size = 2 
maxpool_stride_size = 1 


# input array is 10x10 matrix
data_size=[row_size,col_size]
data_2d = np.random.normal(size=data_size)
x_input_2d = tf.placeholder(dtype=tf.float32,shape=data_size)

# convolutional layer function
# expand data to have batch size = 1, channel size = 1
def conv_layer_2d(input_2d,conv_filter,conv_stride):
    input_3d = tf.expand_dims(input_2d,0)
    input_4d = tf.expand_dims(input_3d,3)
    #return input_4d
            
    convolution_output=tf.nn.conv2d(input_4d,filter=conv_filter,strides=[1,2,2,1],padding="VALID")

    #input_3d = tf.expand_dims(input_2d, 0) 
    #input_4d = tf.expand_dims(input_3d, 3) 

    # Note the stride difference below! 
    #convolution_output = tf.nn.conv2d(input_4d, 
    #                                  filter=conv_filter, 
    #                                  strides=[1, conv_stride, conv_stride, 1],padding="VALID") 

    # Get rid of unnecessary dimensions 
    #return tf.shape(convolution_output) # [1 5 5 1]
    #return tf.shape(tf.squeeze(convolution_output) )
    conv_output_2d = tf.squeeze(convolution_output) # removes extra dimensions so that shape = [5 5]
    
    return conv_output_2d
    
    

# Create filter for convolution.
# note:
# shape of input = [batch, in_height, in_width, in_channels]
# shape of filter = [filter_height, filter_width, in_channels, out_channels]
# Notice that in the input, the width is on the 3rd slot but in the filter, 
# the width is on the 2nd slot
my_filter = tf.Variable(tf.random_normal(shape=[conv_size,conv_size,1,1]))
my_convolution_output = conv_layer_2d(x_input_2d,my_filter,conv_stride=conv_size)


# activation function
def activation(input_2d):
    return tf.nn.relu(input_2d)

my_activation_output = activation(my_convolution_output)

# maxpool
def max_pool(input_2d,width,height,stride):
    input_3d = tf.expand_dims(input_2d,0)
    input_4d = tf.expand_dims(input_3d,3)
    
    # perform max pool
    pool_output = tf.nn.max_pool(input_4d, ksize=[1, height, width, 1], 
                                 strides=[1, stride, stride, 1], 
                                 padding='VALID') 
    
    # Get rid of unnecessary dimensions 
    pool_output_2d = tf.squeeze(pool_output) 
    return pool_output_2d 

# Create Max-Pool Layer 
my_maxpool_output = max_pool(my_activation_output,  
                             width=maxpool_size, 
                             height=maxpool_size, 
                             stride=maxpool_stride_size) 


init = tf.global_variables_initializer() 
sess.run(init) 
feed_dict = {x_input_2d: data_2d}
print('\n>>>> 2D Data <<<<') 

 
# Convolution Output 
print('Input = {} array'.format(x_input_2d.shape.as_list())) 
print('{} Convolution, stride size = [{}, {}], ' 
      'results in the {} array'.format(my_filter.get_shape().as_list()[:2], 
                      conv_stride_size, 
                      conv_stride_size, 
                      my_convolution_output.shape.as_list())) 
print(sess.run(my_convolution_output, feed_dict=feed_dict)) 

 
# Activation Output 
print('\nInput = the above {} array'.format(my_convolution_output.shape.as_list())) 
print('ReLU element wise returns the {} array'.format(my_activation_output.shape.as_list())) 
print(sess.run(my_activation_output, feed_dict=feed_dict)) 

 
# Max Pool Output 
print('\nInput = the above {} array'.format(my_activation_output.shape.as_list())) 
print('MaxPool, stride size = [{}, {}], ' 
    'results in {} array'.format(maxpool_stride_size, 
    maxpool_stride_size, 
    my_maxpool_output.shape.as_list())) 
print(sess.run(my_maxpool_output, feed_dict=feed_dict)) 

#323  # Fully Connected Output 
#324  print('\nInput = the above {} array'.format(my_maxpool_output.shape.as_list())) 
#325  print('Fully connected layer on all {} rows ' 
#326        'results in {} outputs:'.format(my_maxpool_output.shape.as_list()[0], 
#327                                        my_full_output.shape.as_list()[0])) 
#print(sess.run(my_full_output, feed_dict=feed_dict)) 