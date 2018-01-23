'''

    Bryon Kucharski
    Wentorth Institute of Technology
    Spring 2018
    
'''

import numpy as np
from collections import defaultdict

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

        self.q_table = defaultdict(lambda: [0.0,0.0,0.0,0.0])

   
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
        for item in self.q_table.items():
            print(str(item))

    ''' 
    def save_q_table(self, name):
        np.save(name,self.q_table)

    def load_q_table(self, table):
        self.q_table = table
    '''