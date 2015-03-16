'''
Created on Mar 13, 2015

@author: benathi
'''
from pylearn2.config import yaml_parse
import os,sys,inspect
import theano
import numpy as np


def train(yaml_filename):
    current_folder_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    filePath = os.path.join(current_folder_path, 'planktonTest1_conv.yaml')
    print 'Reading YAML Configurations'
    trainObj = open(filePath,'r').read()
    print 'Loading Train Model'
    trainObj = yaml_parse.load(trainObj)
    print 'Looping'
    trainObj.main_loop()
    return trainObj


def trainAndReport():
    import sys
    try:
        yaml_filename = sys.argv[1]
        print 'Loading', yaml_filename
        train(yaml_filename)
    except IndexError:
        print 'Please specify YAML filename in the argument. Eg. python Report.py plankton_conv.yaml'
    

if __name__=='__main__':
    trainAndReport()