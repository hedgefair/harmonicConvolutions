'''MNIST tests'''

'''Test the gConv script'''

import os
import sys
import time

import cv2
import numpy as np
import scipy.linalg as scilin
import scipy.ndimage.interpolation as sciint
import tensorflow as tf

import input_data

from gConv2 import *
from matplotlib import pyplot as plt


# Create model
def conv_Z(x, drop_prob, n_filters, n_classes):
	# Store layers weight & bias
	weights = {
		'w1' : get_weights([3,3,1,n_filters], name='W1'),
		'w2' : get_weights([3,3,n_filters,n_filters], name='W2'),
		'w3' : get_weights([n_filters*6*6,500], name='W3'),
		'out': get_weights([500, n_classes], name='W4')
	}
	
	biases = {
		'b1': tf.Variable(tf.constant(1e-2, shape=[n_filters])),
		'b2': tf.Variable(tf.constant(1e-2, shape=[n_filters])),
		'b3': tf.Variable(tf.constant(1e-2, shape=[500])),
		'out': tf.Variable(tf.constant(1e-2, shape=[n_classes]))
	}
	
	# Reshape input picture
	x = tf.reshape(x, shape=[-1, 28, 28, 1])
	
	# Convolution Layer
	cv1 = conv2d(x, weights['w1'], biases['b1'], name='gc1')
	mp1 = tf.nn.relu(maxpool2d(cv1, k=2))
	
	# Convolution Layer
	cv2 = conv2d(mp1, weights['w2'], biases['b2'], name='gc2')
	mp2 = tf.nn.relu(maxpool2d(cv2, k=2))

	# Fully connected layer
	fc3 = tf.reshape(mp2, [-1, weights['w3'].get_shape().as_list()[0]])
	fc3 = tf.nn.bias_add(tf.matmul(fc3, weights['w3']), biases['b3'])
	fc3 = tf.nn.relu(fc3)
	# Apply Dropout
	fc3 = tf.nn.dropout(fc3, drop_prob)
	
	# Output, class prediction
	out = tf.nn.bias_add(tf.matmul(fc3, weights['out']), biases['out'])
	return out

def gConv_simple(x, drop_prob, n_filters, n_classes):
	# Store layers weight & bias
	weights = {
		'w1' : get_weights([3,3,1,n_filters], name='W1'),
		'w2' : get_weights([3,3,n_filters*4,n_filters], name='W2'),
		'w3' : get_weights([n_filters*6*6,500], name='W3'),
		'out': get_weights([500, n_classes], name='W4')
	}
	
	biases = {
		'b1': tf.Variable(tf.constant(1e-2, shape=[n_filters])),
		'b2': tf.Variable(tf.constant(1e-2, shape=[n_filters])),
		'b3': tf.Variable(tf.constant(1e-2, shape=[500])),
		'out': tf.Variable(tf.constant(1e-2, shape=[n_classes]))
	}
	
	# Reshape input picture
	x = tf.reshape(x, shape=[-1, 28, 28, 1])
	
	# Convolution Layer
	gc1 = gConv(x, weights['w1'], biases['b1'], name='gc1')
	gc1_ = tf.nn.relu(maxpool2d(gc1, k=2))
	
	# Convolution Layer
	gc2 = gConv(gc1_, weights['w2'], biases['b2'], name='gc2')
	gc2_ = coset_pooling(gc2)
	gc2_ = tf.nn.relu(maxpool2d(gc2_, k=2))

	# Fully connected layer
	fc3 = tf.reshape(gc2_, [-1, weights['w3'].get_shape().as_list()[0]])
	fc3 = tf.nn.bias_add(tf.matmul(fc3, weights['w3']), biases['b3'])
	fc3 = tf.nn.relu(fc3)
	# Apply Dropout
	fc3 = tf.nn.dropout(fc3, drop_prob)
	
	# Output, class prediction
	out = tf.nn.bias_add(tf.matmul(fc3, weights['out']), biases['out'])
	return out

def gConv_taco(x, drop_prob, n_filters, n_classes):
	# Store layers weight & bias
	weights = {
		'w1' : get_weights([3,3,1,n_filters], name='W1'),
		'w2' : get_weights([3,3,n_filters*4,n_filters], name='W2'),
		'w3' : get_weights([3,3,n_filters*4,n_filters], name='W3'),
		'w4' : get_weights([3,3,n_filters*4,n_filters], name='W4'),
		'w5' : get_weights([3,3,n_filters*4,n_filters], name='W5'),
		'w6' : get_weights([3,3,n_filters*4,n_filters], name='W6'),
		'w7' : get_weights([3,3,n_filters*4,n_filters], name='W7'),
		'out': get_weights([160, n_classes], name='W4')
	}
	
	biases = {
		'out': tf.Variable(tf.constant(1e-2, shape=[n_classes]))
	}
	
	# Reshape input picture
	xin = tf.reshape(x, shape=[-1, 28, 28, 1])
	
	# Convolution Layerss
	gc1 = tf.nn.relu(gConv(xin, weights['w1'], name='gc1'))
	gc2 = tf.nn.relu(gConv(gc1, weights['w2'], name='gc2'))
	p2_ = maxpool2d(gc2, k=2)
	gc3 = tf.nn.relu(gConv(p2_, weights['w3'], name='gc3'))
	gc4 = tf.nn.relu(gConv(gc3, weights['w4'], name='gc4'))
	gc5 = tf.nn.relu(gConv(gc4, weights['w5'], name='gc5'))
	gc6 = tf.nn.relu(gConv(gc5, weights['w6'], name='gc6'))
	gc7 = tf.nn.relu(gConv(gc6, weights['w7'], name='gc7'))
	
	gc7_ = coset_pooling(gc7)
	gc7_ = tf.reshape(gc7, [-1,160])
	
	# Output, class prediction
	out = tf.nn.bias_add(tf.matmul(gc7_, weights['out']), biases['out'])
	return out

def gConv_steer(x, drop_prob, n_filters, n_classes):
	# Store layers weight & bias
	weights = {
		'w1' : get_weights([1,1,2,n_filters], name='W1'),
		'w2' : get_weights([1,1,2*n_filters,n_filters], name='W2'),
		'w3' : get_weights([n_filters*12*12,500], name='W3'),
		'out': get_weights([500, n_classes], name='W4')
	}
	
	biases = {
		'b1': tf.Variable(tf.constant(1e-2, shape=[n_filters])),
		'b2': tf.Variable(tf.constant(1e-2, shape=[n_filters])),
		'b3': tf.Variable(tf.constant(1e-2, shape=[500])),
		'out': tf.Variable(tf.constant(1e-2, shape=[n_classes]))
	}
	
	# Reshape input picture
	x = tf.reshape(x, shape=[-1, 28, 28, 1])
	
	# Convolution Layer
	sc1 = steer_conv(x, weights['w1'], biases['b1'])
	#mp1 = tf.nn.relu(maxpool2d(sc1, k=2))
	mp1 = tf.nn.relu(sc1)
	
	# Convolution Layer
	sc2 = steer_conv(mp1, weights['w2'], biases['b2'], strides=(1,2,2,1))
	#mp2 = tf.nn.relu(maxpool2d(sc2, k=2))
	mp2 = tf.nn.relu(sc2)

	# Fully connected layer
	fc3 = tf.reshape(mp2, [-1, weights['w3'].get_shape().as_list()[0]])
	fc3 = tf.nn.bias_add(tf.matmul(fc3, weights['w3']), biases['b3'])
	fc3 = tf.nn.relu(fc3)
	# Apply Dropout
	fc3 = tf.nn.dropout(fc3, drop_prob)
	
	# Output, class prediction
	out = tf.nn.bias_add(tf.matmul(fc3, weights['out']), biases['out'])
	return out

def gConv_equi_steer(x, drop_prob, n_filters, n_classes, bs):
	# Store layers weight & bias
	weights = {
		'w1' : get_weights([1,1,2,n_filters], name='W1'),
		'w2' : get_weights([1,1,2*n_filters,n_filters], name='W2'),
		'w3' : get_weights([n_filters*12*12,500], name='W3'),
		'out': get_weights([500, n_classes], name='W4')
	}
	
	biases = {
		'b1': tf.Variable(tf.constant(1e-2, shape=[n_filters])),
		'b2': tf.Variable(tf.constant(1e-2, shape=[n_filters])),
		'b3': tf.Variable(tf.constant(1e-2, shape=[500])),
		'out': tf.Variable(tf.constant(1e-2, shape=[n_classes]))
	}
	
	# Reshape input picture
	x = tf.reshape(x, shape=[bs, 28, 28, 1])
	
	# Convolution Layer
	re1 = equi_steer_conv(x, weights['w1'])
	#mp1 = complex_maxpool2d(re1, k=2)
	nl1 = complex_relu(re1, biases['b1'])

	# Convolution Layer
	re2 = complex_steer_conv(nl1, weights['w2'], strides=(1,2,2,1))
	#mp2 = complex_maxpool2d(re2, k=2)
	nl2 = complex_relu(re2, biases['b2'])

	# Fully connected layer
	nlx, nly = nl2
	R = nlx
	
	fc3 = tf.reshape(R, [bs, weights['w3'].get_shape().as_list()[0]])
	fc3 = tf.nn.bias_add(tf.matmul(fc3, weights['w3']), biases['b3'])
	fc3 = tf.nn.relu(fc3)
	fc3 = tf.nn.dropout(fc3, drop_prob)
	
	# Output, class prediction
	out = tf.nn.bias_add(tf.matmul(fc3, weights['out']), biases['out'])
	return out

def deep_steer(x, drop_prob, n_filters, n_classes, bs):
	# Store layers weight & bias
	weights = {
		'w1' : get_weights([1,1,2,n_filters], name='W1'),
		'w2' : get_weights([1,1,2*n_filters,n_filters], name='W2'),
		'w3' : get_weights([1,1,2*n_filters,n_filters], name='W3'),
		'w4' : get_weights([1,1,2*n_filters,n_filters], name='W3'),
		'w5' : get_weights([n_filters*9*9,500], name='W5'),
		'w6' : get_weights([500, n_classes], name='W6')
	}
	
	biases = {
		'b1': tf.Variable(tf.constant(1e-2, shape=[n_filters]), name='b1'),
		'b2': tf.Variable(tf.constant(1e-2, shape=[n_filters]), name='b2'),
		'b3': tf.Variable(tf.constant(1e-2, shape=[n_filters]), name='b3'),
		'b4': tf.Variable(tf.constant(1e-2, shape=[n_filters]), name='b4'),
		'b5': tf.Variable(tf.constant(1e-2, shape=[500]), name='b5'),
		'b6': tf.Variable(tf.constant(1e-2, shape=[n_classes]), name='b6')
	}
	
	# Reshape input picture
	x = tf.reshape(x, shape=[bs, 28, 28, 1])
	
	# Convolution Layer
	rc1 = equi_steer_conv(x, weights['w1'])
	#nl1 = complex_relu(rc1, biases['b1'])
	cc2 = complex_steer_conv(rc1, weights['w2'])
	#nl2 = complex_relu(cc2, biases['b2'])
	
	cc3 = complex_steer_conv(cc2, weights['w3'], strides=(1,2,2,1))
	#nl3 = complex_relu(cc3, biases['b3'])
	cc4 = complex_steer_conv(cc3, weights['w4'])
	#nl4 = complex_relu(cc4, biases['b4'])
	nlx, __ = cc4

	fc5 = tf.reshape(nlx, [bs, weights['w5'].get_shape().as_list()[0]])
	fc5 = tf.nn.bias_add(tf.matmul(fc5, weights['w5']), biases['b5'])
	fc5 = tf.nn.relu(fc5)
	fc5 = tf.nn.dropout(fc5, drop_prob)
	
	# Output, class prediction
	return tf.nn.bias_add(tf.matmul(fc5, weights['w6']), biases['b6'])

def conv2d(X, V, b=None, strides=(1,1,1,1), padding='VALID', name='conv2d'):
    """conv2d wrapper"""
    VX = tf.nn.conv2d(X, V, strides=strides, padding=padding, name=name+'_')
    if b is not None:
        VX = tf.nn.bias_add(VX, b)
    return VX

def maxpool2d(x, k=2):
    # MaxPool2D wrapper
    return tf.nn.max_pool(x, ksize=[1,k,k,1], strides=[1,k,k,1], padding='SAME')

def get_weights(filter_shape, W_init=None, name='W'):
	if W_init == None:
		stddev = np.sqrt(2.0 / np.prod(filter_shape[:2]))
		W_init = tf.random_normal(filter_shape, stddev=stddev)
	return tf.Variable(W_init, name=name)

def random_rotation(X):
	"""Randomly rotate images, independently in minibatch"""
	X = np.reshape(X, [-1,28,28,1])
	Xsh = X.shape
	for i in xrange(Xsh[0]):
		angle = np.random.rand() * 360.
		M = cv2.getRotationMatrix2D((Xsh[2]/2,Xsh[1]/2), angle, 1)
		X[i,...] = cv2.warpAffine(X[i,...], M, (Xsh[2],Xsh[1])).reshape(Xsh[1:])
	return X.reshape(-1,784)

def run():
	mnist = input_data.read_data_sets("/tmp/data/", one_hot=True)
	
	# Parameters
	lr = 1e-3
	batch_size = 500
	dataset_size = 50000
	valid_size = 5000
	n_epochs = 500
	display_step = dataset_size / batch_size
	save_step = 100
	model = 'deep_steer'
	test_rot = False
	
	# Network Parameters
	n_input = 784 # MNIST data input (img shape: 28*28)
	n_classes = 10 # MNIST total classes (0-9 digits)
	dropout = 0.75 # Dropout, probability to keep units
	n_filters = 10
	
	# tf Graph input
	x = tf.placeholder(tf.float32, [batch_size, n_input])
	y = tf.placeholder(tf.float32, [batch_size, n_classes])
	learning_rate = tf.placeholder(tf.float32)
	keep_prob = tf.placeholder(tf.float32) 
	
	# Construct model
	if model == 'simple_Z':
		pred = conv_Z(x, keep_prob, n_filters, n_classes)
	elif model == 'simple':
		pred = gConv_simple(x, keep_prob, n_filters, n_classes)
	elif model == 'taco':
		pred = gConv_taco(x, keep_prob, n_filters, n_classes)
	elif model == 'steer':
		pred = gConv_steer(x, keep_prob, n_filters, n_classes)
	elif model == 'equi_steer':
		pred = gConv_equi_steer(x, keep_prob, n_filters, n_classes, batch_size)
	elif model == 'deep_steer':
		pred = deep_steer(x, keep_prob, n_filters, n_classes, batch_size)
	else:
		print('Model unrecognized')
		sys.exit(1)

	# Define loss and optimizer
	cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(pred, y))
	#optimizer = tf.train.MomentumOptimizer(learning_rate=lr, momentum=0.9).minimize(cost)
	optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)
	
	# Evaluate model
	correct_pred = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
	accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))
			
	# Initializing the variables
	init = tf.initialize_all_variables()
	
	# Launch the graph
	with tf.Session() as sess:
		sess.run(init)
		step = 1
		start = time.time()
		# Keep training until reach max iterations
		while step < n_epochs * (dataset_size / batch_size):
			batch_x, batch_y = mnist.train.next_batch(batch_size)
			lr_current = lr/np.sqrt(1.+step*(float(batch_size) / dataset_size))
			
			# Optimize
			feed_dict = {x: batch_x, y: batch_y, keep_prob: dropout,
						 learning_rate : lr_current}
			sess.run(optimizer, feed_dict=feed_dict)
			
			if step % display_step == 0:
				# Calculate batch loss and accuracy
				feed_dict = {x: batch_x, y: batch_y, keep_prob: 1.}
				loss, acc = sess.run([cost, accuracy], feed_dict=feed_dict)
				
				# Validation accuracy
				vacc = 0.
				for i in xrange(valid_size/batch_size):
					X = mnist.validation.images[batch_size*i:batch_size*(i+1)]
					Y = mnist.validation.labels[batch_size*i:batch_size*(i+1)]
					if test_rot:
						X = random_rotation(X)
					feed_dict={x : X, y : Y, keep_prob: 1.}
					vacc += sess.run(accuracy, feed_dict=feed_dict)
					#print sess.run(g, feed_dict=feed_dict)[0].shape
					
				print "[" + str(step*batch_size/dataset_size) + \
					"], Minibatch Loss: " + \
					"{:.6f}".format(loss) + ", Train Acc: " + \
					"{:.5f}".format(acc) + ", Time: " + \
					"{:.5f}".format(time.time()-start) + ", Val acc: " + \
					"{:.5f}".format(vacc*batch_size/valid_size)
			step += 1
		
		print "Testing"
		
		# Test accuracy
		tacc = 0.
		for i in xrange(200):
			X = mnist.test.images[50*i:50*(i+1)]
			if test_rot:
				X = random_rotation(X)
			feed_dict={x: X,
					   y: mnist.test.labels[50*i:50*(i+1)], keep_prob: 1.}
			tacc += sess.run(accuracy, feed_dict=feed_dict)
		print('Test accuracy: %f' % (tacc/200.,))


def forward():
	"""Experiment to demonstrate the equivariance of the convolution"""
	mnist = input_data.read_data_sets("/tmp/data/", one_hot=True)
	
	# Network Parameters
	n_input = 784 # MNIST data input (img shape: 28*28)
	n_filters = 10
	
	# tf Graph input
	x = tf.placeholder(tf.float32, [None,28,28,1])
	v0 = tf.placeholder(tf.float32, [1,1,2*1,1])
	v1 = tf.placeholder(tf.float32, [1,1,2*1,1])
	y0, __ = equi_steer_conv_(x, v0)
	y1, __ = equi_steer_conv_(y0, v1)

	# Initializing the variables
	init = tf.initialize_all_variables()
	
	X = mnist.train.next_batch(100)[0][1,:]
	X = np.reshape(X, [1,28,28,1])
	X_ = np.fliplr(X).T
	X = np.stack((X, X_))
	X = X.reshape([2,28,28,1])
	V0 = np.random.randn(1,1,2*1,1).astype(np.float32)
	V1 = np.random.randn(1,1,2*1,1).astype(np.float32)
	
	# Launch the graph
	with tf.Session() as sess:
		sess.run(init)
		Y = sess.run(y1, feed_dict={x : X, v0 : V0, v1 : V1})
	print Y.shape
	Y0 = np.squeeze(Y[0])
	Y1 = np.fliplr(np.squeeze(Y[1])).T
	print("(Y0-Y1)**2: %f" % (np.sum((Y0-Y1)**2),))
	
	fig1 = plt.figure(1)
	plt.imshow(Y0, cmap='gray', interpolation='nearest')
	fig2 = plt.figure(2)
	plt.imshow(Y1, cmap='gray', interpolation='nearest')
	plt.show()

def angular():
	"""Experiment to demonstrate the angular selectivity of the convolution"""
	mnist = input_data.read_data_sets("/tmp/data/", one_hot=True)
	
	# Network Parameters
	n_input = 784 # MNIST data input (img shape: 28*28)
	n_filters = 10
	
	# tf Graph input
	x = tf.placeholder(tf.float32, [None,28,28,1])
	v0 = tf.placeholder(tf.float32, [1,1,2*1,1])
	y = equi_steer_conv_(x, v0)

	# Initializing the variables
	init = tf.initialize_all_variables()
	
	X = mnist.train.next_batch(100)[0][1,:]
	X = np.reshape(X, [1,28,28,1])
	X_ = np.fliplr(X).T
	X = np.stack((X, X_))
	X = X.reshape([2,28,28,1])
	V0 = np.random.randn(1,1,2*1,1).astype(np.float32)
	#V0 = np.ones((1,1,2,1)).astype(np.float32)
	
	# Launch the graph
	with tf.Session() as sess:
		sess.run(init)
		Y, A = sess.run(y, feed_dict={x : X, v0 : V0})
	
	Y0 = np.squeeze(Y[0])
	A0 = np.squeeze(A[0])
	Y1 = np.squeeze(Y[1])
	A1 = np.squeeze(A[1])
	X_0, Y_0 = np.cos(A0), np.sin(A0)
	X_1, Y_1 = np.cos(A1), np.sin(A1)
	
	plt.figure(1)
	plt.imshow(Y0, cmap='jet', interpolation='nearest')
	plt.quiver(X_0, Y_0)
	plt.figure(2)
	plt.imshow(Y1, cmap='jet', interpolation='nearest')
	plt.quiver(X_1, Y_1)
	plt.show()

def real_steer_comparison():
	"""Experiment to demonstrate the angular selectivity of the convolution"""
	mnist = input_data.read_data_sets("/tmp/data/", one_hot=True)
	
	# Network Parameters
	n_input = 784 # MNIST data input (img shape: 28*28)
	n_filters = 10
	
	# tf Graph input
	x = tf.placeholder(tf.float32, [None,28,28,1])
	v0 = tf.placeholder(tf.float32, [1,1,2*1,1])
	#y = equi_steer_conv_(x, v0)
	z = equi_steer_conv(x, v0)

	# Initializing the variables
	init = tf.initialize_all_variables()
	
	X = mnist.train.next_batch(100)[0][1,:]
	X = np.reshape(X, [1,28,28,1])
	X_ = np.fliplr(X).T
	X = np.stack((X, X_))
	X = X.reshape([2,28,28,1])
	V0 = np.random.randn(1,1,2*1,1).astype(np.float32)
	V0 = np.ones((1,1,2,1)).astype(np.float32)
	
	# Launch the graph
	with tf.Session() as sess:
		sess.run(init)
		X, Y = sess.run(z, feed_dict={x : X, v0 : V0})
	
	#R_0 = np.sqrt(np.sum(Y[0,...]**2, axis=2))
	#X_0, Y_0 = np.squeeze(Y[0,:,:,0])/R_0, np.squeeze(Y[0,:,:,1])/R_0
	X = np.squeeze(X)
	Y = np.squeeze(Y)
	R = np.sqrt(X**2 + Y**2)
	X, Y = X/R, Y/R
	
	plt.figure(1)
	plt.imshow(R[0], cmap='gray', interpolation='nearest')
	plt.quiver(X[0], Y[0])
	plt.figure(2)
	plt.imshow(R[1], cmap='jet', interpolation='nearest')
	plt.quiver(X[1], Y[1])
	plt.show()
	
def Z_steer_comparison():
	"""Experiment to demonstrate the angular selectivity of the convolution"""
	mnist = input_data.read_data_sets("/tmp/data/", one_hot=True)
	
	# Network Parameters
	n_input = 784 # MNIST data input (img shape: 28*28)
	n_filters = 10
	
	# tf Graph input
	x = tf.placeholder(tf.float32, [None,28,28,1])
	v = tf.placeholder(tf.float32, [3,3,1,1])
	z = tf.nn.conv2d(x, v, strides=(1,1,1,1), padding='VALID')

	# Initializing the variables
	init = tf.initialize_all_variables()
	
	X = mnist.train.next_batch(100)[0][1,:]
	X = np.reshape(X, [1,28,28,1])
	X_ = np.fliplr(X).T
	X = np.stack((X, X_))
	X = X.reshape([2,28,28,1])
	V = np.random.randn(3,3,1,1).astype(np.float32)
	
	# Launch the graph
	with tf.Session() as sess:
		sess.run(init)
		X = sess.run(z, feed_dict={x : X, v : V})
	
	X = np.squeeze(X)
	X_T = np.flipud(X[1].T)
	
	plt.figure(1)
	plt.imshow(X[0], cmap='gray', interpolation='nearest')
	plt.figure(2)
	plt.imshow(X_T, cmap='gray', interpolation='nearest')
	plt.figure(3)
	plt.imshow(X[0] - X_T, cmap='gray', interpolation='nearest')
	plt.figure(4)
	plt.imshow(np.squeeze(V), cmap='gray', interpolation='nearest')
	plt.show()

def complex_steer_test():
	"""Test the complex convolutional filter"""
	mnist = input_data.read_data_sets("/tmp/data/", one_hot=True)
	
	# Network Parameters
	n_input = 784 
	n_filters = 10
	
	# tf Graph input
	N = 50
	x = tf.placeholder(tf.float32, [N,28,28,1])
	v0 = tf.placeholder(tf.float32, [1,1,2*1,3])
	b0 = tf.placeholder(tf.float32, [3,])
	v1 = tf.placeholder(tf.float32, [1,1,2*3,1])
	
	y = equi_steer_conv(x, v0)
	#mp = complex_maxpool2d(y, k=2)	# For now process R independently everywhere
	#y = complex_relu(mp, b0)
	z = complex_steer_conv(y, v1)

	# Initializing the variables
	init = tf.initialize_all_variables()
	
	X = mnist.train.next_batch(100)[0][1,:]
	X = np.reshape(X, [28,28])
	X_ = []
	
	for i in xrange(N):
		angle = i*(360./N)
		X_.append(sciint.rotate(X, angle, reshape=False))
	X = np.reshape(np.stack(X_), [N,28,28,1])
	
	V0 = np.random.randn(1,1,2*1,3).astype(np.float32)
	B0 = np.random.randn(3).astype(np.float32)-0.5
	V1 = np.random.randn(1,1,2*3,1).astype(np.float32)
	
	# Launch the graph
	with tf.Session() as sess:
		sess.run(init)
		Z = sess.run(z, feed_dict={x : X, v0 : V0, b0 : B0, v1 : V1})
		
	Zx, Zy = Z
	R = np.sqrt(Zx**2 + Zy**2)
	Zx = np.squeeze(Zx/R)
	Zy = np.squeeze(Zy/R)
	R = np.squeeze(R)
	
	plt.figure(1)
	plt.ion()
	plt.show()
	for i in xrange(N):
		plt.cla()
		plt.imshow(R[i], cmap='jet', interpolation='nearest')
		plt.quiver(Zx[i], Zy[i])
		plt.show()
		raw_input(i*(360./N))
	
def complex_small_patch_test():
	"""Test the steer_conv on small rotated patches"""
	N = 50
	X = np.asarray([1.,1.,1.,0.,0.,0.,-1.,-1.,-1.])
	Q = get_Q()
	X = gen_data(X, N, Q)
	X = np.reshape(X, [N,3,3,1])
	
	x = tf.placeholder('float', [None,3,3,1], name='x')
	v0 = tf.placeholder('float', [1,1,2,1], name='v0')
	v1 = tf.placeholder('float', [1,1,2,1], name='v1')
	esc1 = equi_steer_conv(x, v0)
	z = complex_steer_conv(esc1, v1, k=1)
	
	V0 = np.random.randn(1,1,2,1)
	V1 = np.random.randn(1,1,2,1)

	with tf.Session() as sess:
		init_op = tf.initialize_all_variables()
		sess.run(init_op)
		X, Y = sess.run(z, feed_dict={x : X, v0 : V0, v1 : V1})
	
	R = np.sqrt(X**2 + Y**2)
	A = np.arctan2(Y, X)
	fig = plt.figure(1)
	theta = np.linspace(0, 2*np.pi, N)
	plt.plot(theta, np.squeeze(R), 'b')
	plt.plot(theta, np.squeeze(A), 'r')
	plt.show()

def small_patch_test():
	"""Test the steer_conv on small rotated patches"""
	N = 50
	X = np.random.randn(9)	#arange(9)
	Q = get_Q()
	X = gen_data(X, N, Q)
	X = np.reshape(X, [N,3,3,1])
	
	V = np.ones([1,1,2,1])
	V[:,:,1,:] *= 20
	V = V/np.sqrt(np.sum(V**2))
	
	x = tf.placeholder('float', [None,3,3,1], name='x')
	v = tf.placeholder('float', [1,1,2,1], name='v')
	r, a = equi_steer_conv(x, v)
	print V
	with tf.Session() as sess:
		init_op = tf.initialize_all_variables()
		sess.run(init_op)
		X, Y = sess.run([r,a], feed_dict={x : X, v : V})
	
	R = np.sqrt(X**2 + Y**2)
	A = np.arctan2(Y, X)
	fig = plt.figure(1)
	theta = np.linspace(0, 2*np.pi, N)
	plt.plot(theta, np.squeeze(R), 'b')
	plt.plot(theta, np.squeeze(A), 'r')
	plt.show()
	

def gen_data(X, N, Q):
	# Get rotation
	theta = np.linspace(0, 2*np.pi, N)
	Y = []
	for t in theta:
		Y.append(reproject(Q,X,t))
	Y = np.vstack(Y)
	return Y

def get_Q(k=3,n=2):
	"""Return a tensor of steerable filter bases"""
	lin = np.linspace((1.-k)/2., (k-1.)/2., k)
	x, y = np.meshgrid(lin, lin)
	gdx = gaussian_derivative(x, y, x)
	gdy = gaussian_derivative(x, y, y)
	G0 = np.reshape(gdx/np.sqrt(np.sum(gdx**2)), [k*k])
	G1 = np.reshape(gdy/np.sqrt(np.sum(gdx**2)), [k*k])
	return np.vstack([G0,G1])

def reproject(Q, X, angle):
	"""Reproject X through Q rotated by some amount"""
	# Represent in Q-space
	Y = np.dot(Q,X)
	# Rotate
	R = np.asarray([[np.cos(angle), np.sin(angle)],
					[-np.sin(angle), np.cos(angle)]])
	return np.dot(Q.T, np.dot(R,Y))
	
def dot_blade_test():
	v = tf.placeholder('float', [1,1,6,3], 'v')
	v_ = dot_blade_filter(v)

	V = np.random.randn(1,1,6,3)
	
	init = tf.initialize_all_variables()	
	with tf.Session() as sess:
		sess.run(init)
		V_ = sess.run(v_, feed_dict={v : V})

	V, V_ = V_
	print V
	print V_

if __name__ == '__main__':
	run()
	#forward()
	#angular()
	#real_steer_comparison()
	#complex_steer_test()
	#small_patch_test()
	#complex_small_patch_test()
	#dot_blade_test()
	#Z_steer_comparison()