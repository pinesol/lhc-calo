'''
Summary of experiment:
- one generator hit per discriminator hit
- Reduced generator width to 600
- Added two more generator layers
- Changed activation to ReLU
'''
import train

import time
import numpy as np
import tensorflow as tf
import os
import sys
from tensorflow.contrib.layers.python import layers


tf.flags.DEFINE_string("config","default", "The name of the hyperparameter configuration.")
tf.flags.DEFINE_string("exp_name", "", "The name of the experiment. controls the output dir.")
FLAGS = tf.flags.FLAGS


WIDTH = 20 # Image width (X,Y axes)


def generator(z, y):
    '''
    args:
        z: random vector
    returns:
        net: generator network
    '''
    zf = layers.fully_connected(z, 1000, scope='fcz')
    yf = layers.fully_connected(y, 200, scope='fcy')
    net = tf.concat(1, [zf, yf])
    net = layers.fully_connected(net, 600, activation_fn=tf.nn.relu, scope='fc1')
    net = layers.fully_connected(net, 600, activation_fn=tf.nn.relu, scope='fc2')
    net = layers.fully_connected(net, 600, activation_fn=tf.nn.relu, scope='fc3')
    net = layers.fully_connected(net, 600, activation_fn=tf.nn.relu, scope='fc4')
    net = layers.fully_connected(net, WIDTH*WIDTH, scope='fc5')
    return net

def discriminator(x,y):
    '''
    args:
        x: data vector
    returns:
        net: discriminator network
    '''
    xf = layers.fully_connected(x, 1000, scope='fcx')
    yf = layers.fully_connected(y, 200, scope='fcy') 
    net = tf.concat(1, [xf, yf])
    net = layers.dropout(net, 0.2, scope='do1') 
    net = layers.fully_connected(net, 1200, activation_fn=tf.nn.sigmoid, scope='fc1')
    net = layers.dropout(net, 0.5, scope='do2')
    net = layers.fully_connected(net, 1200, activation_fn=tf.nn.sigmoid, scope='fc2')
    net = layers.dropout(net, 0.5, scope='do3')
    # no activation b.c. it's in the cost function used later.
    net = layers.fully_connected(net, 1, scope='fc3', activation_fn=None) 
    return net


class DefaultConfig(object):
    batch_size = 512 #TODO: why not bigger?
    samples_batch_size = 100 #number of samples of each particle type and momentum bin.
    z = 100
    max_epochs = 250
    lr = 0.0002
    beta1=0.5
    momentum = 0.5
    decay_steps = 100000
    decay_factor = 0.96
    train_dir = '/scratch/cdg356/udon/exp/'
    slice_idx = 12
    num_files = 100
    test = False
    generator_hits = 1
    save_freq = 10000

# fewer epochs and bigger batch size so tests are kinda fast. 
class TestConfig(object):
    batch_size = 32
    samples_batch_size = 10 #number of samples of each particle type and momentum bin.
    z = 100
    max_epochs = 2
    lr = 0.0002
    beta1=0.5
    momentum = 0.5
    decay_steps = 100000
    decay_factor = 0.96
    train_dir = '../exp/'
    slice_idx = 12
    
    num_files = 1
    test = True  # This is what tells it to use the test data
    generator_hits = 4
    save_freq = 1

configs_dict = {
    'default': DefaultConfig(),
    'test': TestConfig()
}


def main(argv=None):  # pylint: disable=unused-argument
    FLAGS._parse_flags()
    print("\nParameters:")
    for attr, value in sorted(FLAGS.__flags.items()):
        print("{}={}".format(attr.upper(), value))
    print("")

   
    config = configs_dict[FLAGS.config]
    if FLAGS.exp_name:
        exp_dir = os.path.join(config.train_dir, FLAGS.exp_name)
        if os.path.isdir(exp_dir):
            print 'output dir {} already exists!'.format(exp_dir)
            sys.exit(1)
        config.train_dir = os.path.join(config.train_dir, FLAGS.exp_name)
    else:
        config.train_dir = os.path.join(config.train_dir,
                                        'exp_' + time.strftime("%Y.%m.%d.%H.%M.%S") + '/')
        
    train.build_train_2d(config, generator, discriminator)

if __name__ == '__main__':
    tf.app.run()
