#import matplotlib.pyplot as plt
#import numpy as np
#import tensorflow as tf
#import requests

import matplotlib.pyplot as plt 
import numpy as np 
import tensorflow as tf 
import requests 
import os.path 
import csv 
from tensorflow.python.framework import ops 
 
# Reset computational graph 
ops.reset_default_graph() 
sess = tf.Session()



## load data
## name of data file 
birth_weight_file = 'birth_weight.csv' 
#birthdata_url = 'https://github.com/nfmcclure/tensorflow_cookbook/raw/master/01_Introduction/07_Working_with_Data_Sources/birthweight_data/birthweight.dat' 
#
## Download data and create data file if file does not exist in current directory 
#os.remove(birth_weight_file)
#if not os.path.exists(birth_weight_file): 
#    birth_file = requests.get(birthdata_url) 
#    birth_data = birth_file.text.split('\r\n')
#    
#    
#    birth_header = birth_data[0].split('\t') 
#    birth_data = [[float(x) for x in y.split('\t') if len(x) >= 1] 
#                    for y in birth_data[1:] if len(y) >= 1] 
#    with open(birth_weight_file, "w") as f: 
#        writer = csv.writer(f) 
#        writer.writerows([birth_header]) 
#        writer.writerows(birth_data) 
#        f.close() 

 
 
# read birth weight data into memory 
birth_data = [] 
with open(birth_weight_file, newline='') as csvfile: 
    csv_reader = csv.reader(csvfile) 
    birth_header = next(csv_reader) 
    for row in csv_reader: 
        birth_data.append(row) 
        
birth_data = [[float(x) for x in row] for row in birth_data] 
 
# Pull out target variable 
y_vals = np.array([x[0] for x in birth_data]) 
# Pull out predictor variables 
x_vals = np.array([x[1:8] for x in birth_data]) 

# Set random seed for reproducible results 
seed = 99 
np.random.seed(seed) 
tf.set_random_seed(seed) 


# Declare batch size 
batch_size = 90

# Split data into train/test = 80%/20% 
train_indices = np.random.choice(len(x_vals), round(len(x_vals)*0.8), replace=False) 
test_indices = np.array(list(set(range(len(x_vals))) - set(train_indices))) 
x_vals_train = x_vals[train_indices] 
x_vals_test = x_vals[test_indices] 
y_vals_train = y_vals[train_indices] 
y_vals_test = y_vals[test_indices] 

# Normalize by column (min-max norm) 
def normalize_cols(m): 
    col_max = m.max(axis=0) 
    col_min = m.min(axis=0) 
    return (m-col_min) / (col_max - col_min) 

x_vals_train = np.nan_to_num(normalize_cols(x_vals_train)) 
x_vals_test = np.nan_to_num(normalize_cols(x_vals_test)) 

# Create graph 
sess = tf.Session() 
 
# Initialize placeholders 
x_data = tf.placeholder(shape=[None, 7], dtype=tf.float32) 
y_target = tf.placeholder(shape=[None, 1], dtype=tf.float32) 
 
# Create variable definition 
def init_variable(shape): 
    return tf.Variable(tf.random_normal(shape=shape)) 

 
 # Create a logistic layer definition 
def logistic(input_layer, multiplication_weight, bias_weight, activation=True): 
    linear_layer = tf.add(tf.matmul(input_layer, multiplication_weight), bias_weight) 
    # We separate the activation at the end because the loss function will 
    # implement the last sigmoid necessary 
    if activation: 
        return tf.nn.sigmoid(linear_layer) 
    else: 
        return linear_layer 

nl1 = 5
nl2 = 5
nl3 = 1
 
# First logistic layer (7 inputs to X hidden nodes) 
A1 = init_variable(shape=[7, nl1]) 
b1 = init_variable(shape=[nl1]) 
logistic_layer1 = logistic(x_data, A1, b1) 

 
# Second logistic layer (7 hidden inputs to 5 hidden nodes) 
A2 = init_variable(shape=[nl1, nl2]) 
b2 = init_variable(shape=[nl2]) 
logistic_layer2 = logistic(logistic_layer1, A2, b2) 
#final_output = logistic(logistic_layer1, A2, b2) 
  
 
# 3rd logistic layer (5 hidden nodes to 1 output) 
A3 = init_variable(shape=[nl2, nl3]) 
b3 = init_variable(shape=[nl3]) 
#logistic_layer3 = logistic(logistic_layer2, A3, b3) 
final_output = logistic(logistic_layer2, A3, b3, activation=False) 
  
# final output
# do not return sigmoid on the last layer 
#A4 = init_variable(shape=[nl3, 1]) 
#b4 = init_variable(shape=[1]) 
#final_output = logistic(logistic_layer3, A4, b4, activation=False) 

# Declare loss function (Cross Entropy loss) 
loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=final_output, labels=y_target)) 
 
# Declare optimizer 
my_opt = tf.train.AdamOptimizer(learning_rate=0.001) 
train_step = my_opt.minimize(loss) 
 
# Initialize variables 
init = tf.global_variables_initializer() 
sess.run(init) 
 
# Actual Prediction 
prediction = tf.round(tf.nn.sigmoid(final_output)) 
predictions_correct = tf.cast(tf.equal(prediction, y_target), tf.float32) 
accuracy = tf.reduce_mean(predictions_correct) 

# Training loop 
loss_vec = [] 
train_acc = [] 
test_acc = [] 
for i in range(6500): 
    rand_index = np.random.choice(len(x_vals_train), size=batch_size) 
    rand_x = x_vals_train[rand_index] 
    rand_y = np.transpose([y_vals_train[rand_index]]) 
    sess.run(train_step, feed_dict={x_data: rand_x, y_target: rand_y}) 
 
    temp_loss = sess.run(loss, feed_dict={x_data: rand_x, y_target: rand_y}) 
    loss_vec.append(temp_loss) 

    # accuracy using TRAINED NEURAL NET on training data
    temp_acc_train = sess.run(accuracy, feed_dict={x_data: x_vals_train, y_target: np.transpose([y_vals_train])}) 
    train_acc.append(temp_acc_train) 

    # accuracy using TRAINED NEURAL NET on test data
    temp_acc_test = sess.run(accuracy, feed_dict={x_data: x_vals_test, y_target: np.transpose([y_vals_test])}) 
    test_acc.append(temp_acc_test) 
    
    if (i + 1) % 150 == 0: 
        print('Loss = {}'.format(temp_loss)) 
 
# Plot loss over time 
plt.plot(loss_vec, 'k-') 
plt.title('Cross Entropy Loss per Generation') 
plt.xlabel('Generation') 
plt.ylabel('Cross Entropy Loss') 
plt.ylim([0.0,1.0])
plt.show() 
 
# Plot train and test accuracy 
plt.plot(train_acc, 'k-', label='Train Set Accuracy') 
plt.plot(test_acc, 'r--', label='Test Set Accuracy') 
plt.title('Train and Test Accuracy') 
plt.ylim([0.0,1.0])
plt.xlabel('Generation') 
plt.ylabel('Accuracy') 
plt.legend(loc='lower right') 
plt.show() 
