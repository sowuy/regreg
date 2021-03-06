import numpy as np
import pylab, time, scipy
import scipy.sparse
import regreg.regression as regreg
import regreg.lasso as lasso
import regreg.graphnet as graphnet
import regreg.lin_graphnet as lin_graphnet
import regreg.signal_approximator as glasso
from tests import gen_adj        
import nose.tools

control = {'max_its':500,
           'tol':1.0e-8,
           'plot':False,
           'backtrack':True}

def test_lin_graphnet(X=None,Y=None,l1=25.,l2=0.,l3=1., control=control,nonneg=False):

    if X is None or Y is None:
        X = np.load('X.npy')
        Y = np.load('Y.npy')


    p = X.shape[1]
    _ , L = gen_adj(p)
    Lsparse = scipy.sparse.lil_matrix(L)

    #np.random.shuffle(Y)
    Y = np.dot(Y,X)
    np.random.shuffle(Y)
    #Y = np.random.normal(0,1,X.shape[1])
    
    l1 *= X.shape[0]
    if nonneg:
        p1 = lin_graphnet.gengrad_nonneg((Y, L))
    else:
        p1 = lin_graphnet.gengrad((Y, L))

    p1.assign_penalty(l1=l1,l2=l2,l3=l3)
    t1 = time.time()
    opt1 = regreg.FISTA(p1)
    #opt1.debug = True
    opt1.fit(tol=control['tol'], max_its=control['max_its'])
    beta1 = opt1.problem.coefs
    t2 = time.time()
    ts3 = t2-t1

    if nonneg:
        p2 = lin_graphnet.gengrad_nonneg_sparse((Y, Lsparse))
    else:
        p2 = lin_graphnet.gengrad_sparse((Y, Lsparse))
    p2.assign_penalty(l1=l1,l2=l2,l3=l3)
    t1 = time.time()
    opt2 = regreg.FISTA(p2)
    opt2.fit(tol=control['tol'], max_its=control['max_its'])
    beta2 = opt2.problem.coefs
    t2 = time.time()
    ts3 = t2-t1



    def f(beta):
        if np.min(beta) < 0 and nonneg:
            return np.inf
        else:                
            return - np.dot(Y, beta) + np.fabs(beta).sum()*l1 + l2 * np.linalg.norm(beta)**2 + l3 * np.dot(beta, np.dot(L, beta))
    
    v = scipy.optimize.fmin_powell(f, np.zeros(len(Y)), ftol=1.0e-10, xtol=1.0e-10,maxfun=100000)
    v = np.asarray(v)


    N = 10000
    print np.round(N*beta1)/N
    print np.round(N*beta2)/N
    print np.round(N*v)/N
    print f(beta1), f(v)

