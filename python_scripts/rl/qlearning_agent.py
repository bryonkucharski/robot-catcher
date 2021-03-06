'''

    Bryon Kucharski
    Wentorth Institute of Technology
    Spring 2018
    
'''

import numpy as np
import math
import os, sys, inspect
from collections import defaultdict
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import RMSprop

#this is just to import stddraw from a different folder
princeton_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../princeton_lib")))
if princeton_subfolder not in sys.path:
    sys.path.insert(0, princeton_subfolder)

import stddraw
import color

class rl_agent:
    
    def __init__(self,A,gamma,alpha,epsilon):
        '''
        Constructor

        ARGS:
            A: a list of actions the agent has the possibility to take
                ex - [0,1,2,3] for up,down,right,left
            gamma: the discount factor. How much the Q(s',a') is taken into consideration when updating the q table
            alph: the learning rate. How fast the agent learns
            epsilon: 'greediness' of the agent. How often the agent should explore vs follow the q table
        '''

        #self.states = S
        self.actions = A
        self.gamma = gamma
        self.alpha = alpha
        self.epsilon = epsilon

    
    def init_q_table(self):
        '''
        the q table is a defaultdict. The lambda expression is fancy for saying "Everytime a new row (state) is added to the table, initalize the values as 0
        *to use the default dict the state must be in a string 
            ex - 
           
                d = defaultdict(lambda: [0.0,0.0,0.0,0.0])
            
                state = str([0,1])
                row = d[state]
                print(row) #returns [0.0,0.0,0.0,0.0], or whatever is in lambda function

                num = d[state][0]
                print(num) # returns 0 

                d[state][0] = 10

                row = d[state]
                print(row) #returns [10,0.0,0.0,0.0], or whatever is in lambda function
                
                num = d[state][0]
                print(num) # returns 10

        '''
        #self.q_table = defaultdict(lambda: [0.0,0.0,0.0,0.0])


        self.q_table = defaultdict(lambda: [0.0 for x in range(len(self.actions)) ])

    def init_NN(sef,num_outputs, size):
        
        model = Sequential()

        model.add(Dense(164, input_shape=(size,)))
        model.add(Activation('relu'))

        model.add(Dense(150))
        model.add(Activation('relu'))

        model.add(Dense(4))
        model.add(Activation('linear')) #linear output so we can have range of real-valued outputs

        rms = RMSprop()
        model.compile(loss='mse', optimizer=rms)
        return model

        

    def get_NN_action(self, model,state):
        '''
        picks an action with the highest q value generated from a neural network
        or picks random action

        ARGS:
            model: keras model to fit
            state: state as form (state, 1)
  
        RETURNS:   
            self.epsilon % of the time - One of the actions defined in self.actions with the highest Q value 
            1-self.epsilon % of the time - a random action
        '''
        qvals = model.predict(state, batch_size= 1)
        if np.random.rand() < self.epsilon:
            return np.argmax(qvals), qvals
        else:
            return np.random.choice(self.actions), qvals

    def update_NN(self, s, a, r, s_, qvals, model):
        newQ = model.predict(s_, batch_size=1)
        maxQ = np.max(newQ)
        
        y = np.zeros((1,len(self.actions)))
 
        y[:] = qvals[:]
        
        update = (r + (self.gamma * maxQ))
        y[0][a] = update
        model.fit(s, y, batch_size=1, epochs=1, verbose=0)
        
    def get_q_table(self):
        return self.q_table

    def update(self, s, a, r, s_):
        '''
        update the q table at the given state, action point

        ARGS:
            s: current state of the environment
            a: action just taken in the environment
            r: reward from the action just taken in the enviornment
            s_: the next state, after taking the action
        '''
       
        exp = max(self.q_table[s_]) # determine the expected value of the next step
        current = self.q_table[s][a]  # determmine the current value of the current step

        '''
        #For debugging
        print('current q: ' + str(current))
        print('current a : ' + str(a))
        print('r : ' + str(r))
        print('s: ' + str(s))
        print('s_: ' + str(s_))
        #print('a_: ' + str(a_))
        print('exp: ' + str(exp))
        '''
       
        self.q_table[s][a] =  current + self.alpha * ( r + self.gamma * (exp) - current)  # update the spot in the q table    
        
    def get_action(self, state):
        '''
        go to colum of given state
        pick action with highest q value

        ARGS:
            state = list of current state as a string 
                ex - str([0,0])
        RETURNS:   
            self.epsilon % of the time - One of the actions defined in self.actions with the highest Q value 
            1-self.epsilon % of the time - a random action
        '''
        if np.random.rand() < self.epsilon:
            row = self.q_table[state]
            action = np.argmax(row)
        else:
            action = np.random.choice(self.actions)

        return action
    
    def print_q_table(self):
        '''
        prints all values currently in the q table
        '''

        for item in sorted(self.q_table.items()):
            print(str(item))
    

    def init_stddraw(self, width):
        stddraw.setXscale(0, width)
        stddraw.setYscale(0, width)
        stddraw.setCanvasSize(width,width)

    def visualize_q_table(self, width):

        qt = sorted(self.q_table.items())
        GRID_SIZE_X = width / len(self.actions)
        GRID_SIZE_Y = width / len(qt)

        for i in range(0,len(self.q_table.items())):
           
            for j in range(0,len(self.actions)):
                #print(str(qt[i][1][j]) + ' ',end='')
                current_val = (qt[i][1][j]) 
                sigmoid = 1 / (1 + math.exp(-current_val)) #get a range between 0 and 1
                state_name = qt[i][0] + " - " + str(round(qt[i][1][j],2))
                if current_val < 0:
                    new_color = color.Color(int(sigmoid*255),0,0)
                elif current_val == 0.0:
                    new_color = color.Color(0,0,0)
                else:
                    new_color = color.Color(0,int(sigmoid*255),0)
                #stddraw.setPenColor(color.BLACK)
                #stddraw.text((GRID_SIZE_X * i) + (GRID_SIZE/2),(GRID_SIZE * j) + (GRID_SIZE / 2), state_name)
               
                stddraw.setPenColor(new_color)
                stddraw.filledRectangle( (GRID_SIZE_X*j),width - (GRID_SIZE_Y*i) - GRID_SIZE_Y,GRID_SIZE_X,GRID_SIZE_Y)
                stddraw.setPenColor(color.WHITE)
                stddraw.text((GRID_SIZE_X*j) + (GRID_SIZE_X/2),width - (GRID_SIZE_Y*i) - GRID_SIZE_Y + (GRID_SIZE_Y/2), state_name)
        
        stddraw.setPenColor(color.BLACK)
        #gridlines
        for i in range(1,len(self.q_table.items())):
            stddraw.filledRectangle(0,GRID_SIZE_Y*i,width,0)

        for i in range(1,len(self.actions)):
            stddraw.filledRectangle(GRID_SIZE_X * i,0,0,width)

        stddraw.show(0)


    ''' 
    def save_q_table(self, name):
        np.save(name,self.q_table)

    def load_q_table(self, table):
        self.q_table = table
    '''