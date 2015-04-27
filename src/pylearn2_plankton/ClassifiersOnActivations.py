'''
Created on Apr 18, 2015

@author: ben
'''
import numpy as np
import pickle, os
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm

'''
Note: format of Y_train is 
'''
def trainRF(X_train, Y_train, X_test, Y_test, model_name, cache=False, n_estimators=500):
    rf_filename = model_name.split('.')[0] + str('RFmodel.p')
    print 'CNN model name', model_name
    print 'Training RF - RF Model Filename =', rf_filename
    if cache:
        if os.path.isfile(rf_filename):
            print 'Model Exists - Loading from disk'
            return pickle.load(open(rf_filename,'rb'))
    print 'number of estimators =', n_estimators
    rf_clf = RandomForestClassifier(n_estimators=n_estimators
                                    ,criterion='gini' # gini
                                    )
    # try lower n_estimator and max_depth=10 (currently no max depth)
    # criterion choice: entropy versys gini
    rf_clf.fit(X_train, Y_train)
    if cache:
        print 'Saving Model to Disk'
        pickle.dump(rf_clf, open(rf_filename, 'wb'))
        print 'Done Saving Model to Disk'
    predictionScores(rf_clf, X_test, Y_test)

def trainSVM(X_train, Y_train, X_test, Y_test, model_name, cache=False, one_vs_rest=True):
    rf_filename = model_name.split('.')[0] + str('RFmodel.p')
    print 'CNN model name', model_name
    print 'Training SVM -SVM Model Filename =', rf_filename
    if cache:
        if os.path.isfile(rf_filename):
            print 'Model Exists - Loading from disk'
            return pickle.load(open(rf_filename,'rb'))
    if one_vs_rest:
        print 'One Versus Rest SVM'
        svm_clf = svm.LinearSVC()       # one versus rest
    else:
        print 'One Versus One SVM'
        svm_clf = svm.SVC()             # one versus one
    svm_clf.fit(X_train, Y_train)   
    if cache:
        print 'Saving Model to Disk'
        pickle.dump(svm_clf, open(rf_filename, 'wb'))
        print 'Done Saving Model to Disk'
    predictionScores(svm_clf, X_test, Y_test)


def findActivations(model_name, listX_raw, which_layer, maxPixel):
    # 1. load model file
    import theano
    from pylearn2.utils import serial
    model = serial.load(model_name)
    print 'Model input space is ', model.get_input_space()
    
    # 2. find activations at that layer
    num_x = len(listX_raw)
    activation_list = []
    for X in listX_raw:
        m = X.shape[0]
        X = np.reshape(X, (m,1,maxPixel, maxPixel))
        X = np.swapaxes(X,1,2)
        X = np.swapaxes(X,2,3)
        print 'XReport type = {}. Dimension = {}'.format(type(X), np.shape(X))
        activation = None
        batch_size = 100
        for batchIndex in range(m/batch_size):
            _input = np.array(X[batchIndex*batch_size:(batchIndex+1)*batch_size],
                    dtype=theano.config.floatX)
        fprop_results = model.fprop(theano.shared(_input,
                            name='XReport'), return_all=True)[which_layer].eval()
        '''
        f1 = fprop_results[0].eval()
        print 'f1=', f1.shape
        f2 = fprop_results[1].eval()
        print 'f2=', f2.shape
        f3 = fprop_results[2].eval()
        print 'f3=', f3.shape
        '''
        print "shape of fprop_results = ", fprop_results.shape
        #print 'shape of fprop', fprop_results.shape
        print 'Returning - DEBUG'             
        return 
        if activation is None:
            activation = fprop_results
        else:
            activation = np.concatenate((activation, fprop_results), axis=0)
        print 'Breaking for debug!!!!'
        break 
            
        
        activation_list.append(activation)
    
    return activation_list

'''
    designMatrix_train = np.array(np.reshape(designMatrix, 
        (ds.get_num_examples(), 1, 28, 28) ), dtype=np.float32)
'''

def getRawData(data_spec, which_set, maxPixel):
    print 'Loading Raw Data set', which_set
    PC = __import__('pylearn2_plankton.planktonDataConsolidated', fromlist=['planktonDataConsolidated'])
    ds = PC.PlanktonData(which_set, maxPixel)
    designMatrix = ds.get_data()[0] # index 1 is the label
    Y = ds.get_data()[1]
    Y = np.where(Y)[1]
    return (designMatrix, Y)
    
'''
Return both X (activations) and Y
Note: configured for 28 x 28 and 3 layer model for now
'''
def prepXY(model_name, data_spec, which_layer, maxPixel):
    # 1. get data
    rawX_train, Y_train = getRawData(data_spec, 'train', maxPixel)
    rawX_cv, Y_cv = getRawData(data_spec, 'valid', maxPixel)
    rawX_test, Y_test = getRawData(data_spec, 'test', maxPixel)
    # combine CV to test
    rawX_train = np.concatenate((rawX_train, rawX_cv), axis=0)
    Y_train = np.concatenate((Y_train, Y_cv), axis=0)
    X_train, X_test = findActivations(model_name, [rawX_train, rawX_test], which_layer, maxPixel)
    # 2. find activations
    print 'Done Finding Activations'
    return (X_train, Y_train, X_test, Y_test)

'''
rf_cl:     random forest classifier as a function
X_test:    design matrix
Y_test:    Does it work for one-hot?
'''
def predictionScores(cl, X_test, Y_test):
    print 'Accuracy Score = ', cl.score(X_test, Y_test)

def rfOnActivationsPerformance(model_name, data_spec, which_layer, maxPixel):
    X_train, Y_train, X_test, Y_test= prepXY(model_name, data_spec, which_layer, maxPixel)
    for i in range(10):
        print 'RF Trial', i
        trainRF(X_train, Y_train, X_test, Y_test, model_name)
    trainSVM(X_train, Y_train, X_test, Y_test, model_name, one_vs_rest=True)
    trainSVM(X_train, Y_train, X_test, Y_test, model_name, one_vs_rest=False)
    
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-layer', action="store", default=2, type=int)
    #parser.add_argument('-yaml', action="store", default='plankton_conv_visualize_model.yaml')
    parser.add_argument('-pklname', action="store", default='model_files/plankton_conv_visualize_model.pkl')
    parser.add_argument('-data', action="store", default='pylearn2_plankton.planktonDataPylearn2')
    parser.add_argument('-maxpix', action="store", default=28, type=int)
    allArgs = parser.parse_args()
    rfOnActivationsPerformance(model_name=allArgs.pklname,
                               data_spec=allArgs.data,
                               which_layer=allArgs.layer,
                               maxPixel=allArgs.maxpix)