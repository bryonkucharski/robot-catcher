
'''
    This class is heavily from https://github.com/keon/deep-q-learning
    Modified by Bryon Kucharski 
    Summer 2018
'''

import random
import numpy as np
from collections import deque
from keras.initializers import normal, identity
from keras.models import model_from_json
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.optimizers import SGD , Adam
import json
import time
from keras.callbacks import TensorBoard


class DQNAgent:
    
    def __init__(self, state_size, action_size, gamma, epsilon, epsilon_min, epsilon_decay, learning_rate, model_type):
        self.max_memory = 2000
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=self.max_memory)
        self.gamma = gamma#0.95    # discount rate
        self.epsilon = epsilon # 1.0  # exploration rate
        self.epsilon_min = epsilon_min# 0.01
        self.epsilon_decay = epsilon_decay # 0.995
        self.learning_rate = learning_rate # 0.001
        #self.tensorboard = TensorBoard(log_dir="logs/{}".format(time()))

        if model_type == 'DeepMind':
            self.model = self.DeepMindModel()
        elif model_type == 'DeepModel':
            self.model = self.DeepModel()

    def DeepModel(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(20, input_shape=((self.state_size,)), activation='relu'))
        model.add(Dense(18, activation='relu'))
        model.add(Dense(10, kernel_initializer='uniform', activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))

        

        return model

    def DeepMindModel(self):
        
        model = Sequential()
        
        model.add(Conv2D(32, 8, 8, subsample=(4, 4), border_mode='same',input_shape=(80,80,4)))  #80*80*4
        model.add(Activation('relu'))
        model.add(Conv2D(64, 4, 4, subsample=(2, 2), border_mode='same'))
        model.add(Activation('relu'))
        model.add(Conv2D(64, 3, 3, subsample=(1, 1), border_mode='same'))
        model.add(Activation('relu'))
        model.add(Flatten())
        model.add(Dense(512))
        model.add(Activation('relu'))
        model.add(Dense(self.action_size))

        adam = Adam(lr=1e-6)
        model.compile(loss='mse',optimizer=adam)
        

        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        if len(self.memory) > self.max_memory:
            del self.memory[0]

    def take_action(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns action

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + self.gamma * np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            target_f[0][action] = target
            
            #tensorboard = TensorBoard(log_dir='./Graph', histogram_freq=0, write_graph=True, write_images=True)
            history = self.model.fit(state, target_f, epochs=1, verbose=0)


        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            
        return history
        
    def predict(self, state): 
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns action 

    def train(self, X_batch, y_batch):
        return self.model.train_on_batch(X_batch, y_batch)[0] #may not need the [0]

    def load(self, name):
        print("Loading Model")
        self.model.load_weights(name)

    def save(self, name):
        print("Saving Model")
        self.model.save_weights(name)

    def memory_length(self):
        return len(self.memory)

    def print_model_weights(self):
        i = 0
        for layer in self.model.layers:
            i +=1
            weights = layer.get_weights() # list of numpy arrays
            print("Layer " + str(i) + ": " + str(weights))
            