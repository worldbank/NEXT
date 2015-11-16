"""
LUCB app implements CardinalBanditsPureExplorationPrototype
author: Kevin Jamieson
last updated: 11/13/2015
"""

import numpy
import numpy.random
from next.apps.CardinalBanditsPureExploration.Prototype import CardinalBanditsPureExplorationPrototype

class LUCB(CardinalBanditsPureExplorationPrototype):

  def initExp(self,resource,n,R,failure_probability):
    """
    initialize the experiment 

    Expected input:
      (next.database.ResourceClient) resource : database client, can cell resource.set(key,value), value=resource.get(key) 
      (int) n : number of arms
      (float) R : sub-Gaussian parameter, e.g. E[exp(t*X)]<=exp(t^2 R^2/2), defaults to R=0.5 (satisfies X \in [0,1])
      (float) failure_probability : confidence

    Expected output (comma separated):
      (boolean) didSucceed : did everything execute correctly
    """
    resource.set('n',n)
    resource.set('failure_probability',failure_probability)
    resource.set('R',R)
    resource.increment('total_pulls',0)
    for i in range(n):
      resource.increment('Xsum_'+str(i),0.)
      resource.increment('X2sum_'+str(i),0.)
      resource.increment('T_'+str(i),0)

    return True

  
  def getQuery(self,resource,do_not_ask_list):
    """
    A request to ask which index/arm to pull

    Expected input:
      (next.database.DatabaseClient) resource : database client, can cell resource.set(key,value), value=resource.get(key)
      (list int) do_not_ask_list : list of indices that are not desired to be asked. 
    Expected output (comma separated): 
      (int) target_index : idnex of arm to pull (in 0,n-1)
    """
    n = resource.get('n')

    key_list = ['R','failure_probability']
    for i in range(n):
      key_list.append( 'Xsum_'+str(i) )
      key_list.append( 'T_'+str(i) )

    key_value_dict = resource.get_many(key_list)

    R = key_value_dict['R']
    delta = key_value_dict['failure_probability']

    sumX = []
    T = []
    for i in range(n):
      sumX.append( key_value_dict['Xsum_'+str(i)] )
      T.append( key_value_dict['T_'+str(i)] )

    T = numpy.array(T)
    mu = numpy.zeros(n)
    UCB = numpy.zeros(n)
    A = []
    for i in range(n):
      if T[i]==0:
        mu[i] = float('inf')
        UCB[i] = float('inf')
        A.append(i)
      else:
        mu[i] = sumX[i] / T[i]
        UCB[i] = mu[i] + numpy.sqrt( 2.0*R*R*numpy.log( 4*T[i]*T[i]/delta ) / T[i] )

    if len(A)>0:
      priority_list = numpy.random.permutation(A)
      k = 0
      while k<len(priority_list) and (priority_list[k] in do_not_ask_list): 
        k+=1
      if k==len(priority_list):
        index = numpy.random.randint(n)
      else:
        index = priority_list[k]
    else:
      # with equal probability choose empirical maximizer and upper confidence bound that is not emp max
      # emp_max_index = numpy.argmax(mu)

      priority_list = numpy.argsort(-mu)
      k = 0
      while k<len(priority_list) and (priority_list[k] in do_not_ask_list): 
        k+=1
      if k==len(priority_list):
        return numpy.random.randint(n)  # no more to ask! just return
      emp_max_index = priority_list[k]

      if numpy.random.rand()<0.5:
        index = emp_max_index
      else:
        # ask for biggest UCB that is not equal to empirical max or in do_not_ask_list
        # if you are here, emp_max_index is not in do_not_ask_list already
        do_not_ask_list.append(emp_max_index)

        priority_list = numpy.argsort(-UCB)
        k = 0
        while k<len(priority_list) and (priority_list[k] in do_not_ask_list): 
          k+=1
        if k==len(priority_list):
          index = numpy.random.randint(n)
        else:
          index = priority_list[k]

    return index

  def processAnswer(self,resource,target_index,target_reward):
    """
    reporting back the reward of pulling the arm suggested by getQuery

    Expected input:
      (next.database.DatabaseClient) resource : database client, can cell resource.set(key,value), value=resource.get(key) 
      (int) target_index : index of arm pulled
      (int) target_reward : reward of arm pulled

    Expected output (comma separated): 
      (boolean) didSucceed : did everything execute correctly
    """    
    resource.increment_many({'Xsum_'+str(target_index):target_reward,'X2sum_'+str(target_index):target_reward*target_reward,'T_'+str(target_index):1,'total_pulls':1})
    
    return True

  def predict(self,resource):
    """
    uses current model to return empirical estimates with uncertainties

    Expected input:
      (next.database.DatabaseClient) resource : database client, can cell resource.set(key,value), value=resource.get(key) 

    Expected output: 
      (list float) mu : list of floats representing the emprirical means
      (list float) prec : list of floats representing the precision values (standard deviation)
    """
    n = resource.get('n')

    key_list = ['R']
    for i in range(n):
      key_list.append( 'Xsum_'+str(i) )
      key_list.append( 'X2sum_'+str(i) )
      key_list.append( 'T_'+str(i) )

    key_value_dict = resource.get_many(key_list)

    R = key_value_dict['R']
    
    sumX = []
    sumX2 = []
    T = []
    for i in range(n):
      sumX.append( key_value_dict['Xsum_'+str(i)] )
      sumX2.append( key_value_dict['X2sum_'+str(i)] )
      T.append( key_value_dict['T_'+str(i)] )

    mu = numpy.zeros(n)
    prec = numpy.zeros(n)
    for i in range(n):
      if T[i]<2 or mu[i]==float('inf'):
        mu[i] = -1
        prec[i] = -1
      else:
        mu[i] = float(sumX[i]) / T[i]
        prec[i] = numpy.sqrt( float( max(R*R,sumX2[i] - T[i]*mu[i]*mu[i]) ) / ( T[i] - 1. ) / T[i] )
    
    return mu.tolist(),prec.tolist()


