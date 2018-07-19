
'''
    Creates a gridworld version of a 1D robot
    Modified by Bryon Kucharski 
    Summer 2018
'''


import os, sys, inspect
from random import randint
import numpy as np
import matplotlib.pyplot as plt
from PIL import ImageGrab
import numpy as np
import matplotlib.pyplot as plt
import time
import cv2

from PIL import Image
import mss #pip install --upgrade mss
import mss.tools


#set sttdraw to 0,0 so you can use vision to get a screenshot
os.environ['SDL_VIDEO_WINDOW_POS'] = str(0) + "," + str(0)


#this is just to import stddraw from a different folder
princeton_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../princeton_lib")))
if princeton_subfolder not in sys.path:
    sys.path.insert(0, princeton_subfolder)

import stddraw

class simulated_1D_robot:
    
    def __init__(self, goalie_pos_start, GRID_NUM_HEIGHT = 8, GRID_NUM_WIDTH = 5, GRID_SIZE = 75, draw_scene = True, gridworld = False):
        self.goalie_pos = goalie_pos_start
        self.GRID_NUM_HEIGHT = GRID_NUM_HEIGHT
        self.GRID_NUM_WIDTH = GRID_NUM_WIDTH
        self.GRID_SIZE = GRID_SIZE
        self.WIDTH = self.GRID_SIZE*self.GRID_NUM_WIDTH
        self.HEIGHT = self.GRID_SIZE*self.GRID_NUM_HEIGHT
        self.num_interations = 0
        self.draw_scene = draw_scene
        self.gridworld = gridworld

        self.ball_radius = GRID_SIZE/2
        
        self.reset()

        if self.draw_scene:
            stddraw.setXscale(0, self.WIDTH)
            stddraw.setYscale(0, self.HEIGHT)
            stddraw.setCanvasSize(self.WIDTH,self.HEIGHT)
        time.sleep(1)

        
        
            

    def drawGridScene(self):
        """
        Draws the gridlines and current position of the ball and robot
        """

        stddraw.clear()
        stddraw.setPenColor(stddraw.BLACK)
        
        #gridlines
        for i in range(1,self.GRID_NUM_HEIGHT):
            stddraw.filledRectangle(0,self.GRID_SIZE*i,self.WIDTH,0)

        for i in range(1,self.GRID_NUM_WIDTH):
            stddraw.filledRectangle(self.GRID_SIZE * i,0,0,self.HEIGHT)

        #goalie
        stddraw.setPenColor(stddraw.BLUE)
        stddraw.filledRectangle(self.goalie_pos*self.GRID_SIZE,0,self.GRID_SIZE,self.GRID_SIZE) #x,y,size_x,size_y
        
        #Ball
        stddraw.setPenColor(stddraw.GREEN)
        stddraw.filledCircle(((self.ball_x *self.GRID_SIZE) + (self.ball_radius)) ,(self.HEIGHT - ((self.ball_y *self.GRID_SIZE) + (self.ball_radius))), self.ball_radius)

        stddraw.show(0)

    def drawNoGridScene(self):
        """
        Draws the current position of the ball and robot
        """

        stddraw.clear()
        stddraw.setPenColor(stddraw.BLACK)

        #goalie
        stddraw.setPenColor(stddraw.BLUE)
        stddraw.filledRectangle(self.goalie_pos*self.GRID_SIZE,0,self.GRID_SIZE,self.GRID_SIZE) #x,y,size_x,size_y
        
        #Ball
        stddraw.setPenColor(stddraw.GREEN)
        stddraw.filledCircle(self.ball_x ,self.HEIGHT - self.ball_y, self.ball_radius)

        stddraw.show(0)

    def get_ball_pos(self):
        """
        Get the x and y position of the ball

        Returns:
            A Tuple of ballx, bally
        """
        return [self.ball_x, self.ball_y]

    def reset(self):
        """
            Resets ball back to top of ramp and a random position in the x location
        """
        if self.gridworld:
            self.ball_x = randint(0, self.GRID_NUM_WIDTH-1)
            self.ball_y = 0
        else:
            self.ball_x = randint(round(self.ball_radius),round(self.WIDTH - self.ball_radius))
            self.ball_y = self.ball_radius

    def get_state_array(self):
        """
         Get the state of the robot in array form, with index 0 being the ball's x location and index 1 being the goalie's x position
        """
        return [self.ball_x, self.goalie_pos]

    def get_state_matrix(self):
        """
        Get the state of the robot in matrix form, with 1 being the location of the ball, 2 being the location of the robot, and 0 being nothing 

        Returns:
            A matrix size (1,GRID_NUM_HEIGHT*GRID_NUM_WIDTH)
        """
        #creates an empty array of the state, everything initalized to 0
        state = np.zeros((self.GRID_NUM_HEIGHT, self.GRID_NUM_WIDTH))
        
        #draws the ball/robot in the correct position of the matrix
        state[ self.ball_y -1, self.ball_x-1 ] = 1 #draws the ball
        state[self.GRID_NUM_HEIGHT - 1, self.goalie_pos] = 2 #draws the robot
        return state.reshape((1,-1))
    
    def get_state_stacked(self, previous_state = None,initalState = False):
        #TODO: Put this in vision file
        
        #screenImage = ImageGrab.grab(bbox=(0, 0, self.WIDTH, self.HEIGHT)).convert('RGB')#(X, Y) starting position ; (W, H) ending position

        with mss.mss() as sct:
        # Use the 1st monitor
            monitor = {'top': 0, 'left': 0, 'width': self.WIDTH, 'height': self.HEIGHT}
            # Get raw pixels from the screen, save it to a Numpy array
            img = np.array(sct.grab(monitor))

        
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

    
    #    cv2.imshow('test',self.get_binary_image())
       
        resized_img = cv2.resize(gray_image, (80,80))
        resized_img = resized_img / 255
       
        if initalState:
            state = np.stack((resized_img, resized_img, resized_img, resized_img), axis=2)
            state = state.reshape(1, state.shape[0], state.shape[1], state.shape[2])  #1*80*80*4
        else:
            resized_img = resized_img.reshape(1, resized_img.shape[0], resized_img.shape[1], 1) #1x80x80x1
            state = np.append(resized_img, previous_state[:, :, :, :3], axis=3)


                          
        return state
        
    def get_state_binary(self, resize_shape):
        with mss.mss() as sct:
        # Use the 1st monitor
            monitor = {'top': 0, 'left': 0, 'width': self.WIDTH, 'height': self.HEIGHT}
            # Get raw pixels from the screen, save it to a Numpy array
            img = np.array(sct.grab(monitor))


        ## convert to hsv
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        ## mask of green (36,0,0) ~ (70, 255,255)
        mask1 = cv2.inRange(hsv, (36, 0, 0), (70, 255,255))

        ## mask o yellow (15,0,0) ~ (36, 255, 255)
        blue_lower=np.array([100,150,0],np.uint8)
        blue_upper=np.array([140,255,255],np.uint8)
        mask2 = cv2.inRange(hsv,blue_lower,blue_upper )
        ## final mask and masked
        mask = cv2.bitwise_or(mask1, mask2)
        resized_img = cv2.resize(mask, resize_shape)
        #cv2.imshow('test',resized_img)
        return resized_img.reshape((1,-1))  
    
    def step(self, action, stateType = 'array', previous_state = None, reshape_shape = None ):
        """
        Takes one step of the environment. The ball moves down the ramp, an action is taken by the robot which results in a new state.

        Args:
            action: the action the robot wants to take
            stateType: type of state to return as state_prime, either array or matrix 
        Returns:
            Tuple of -
                s : state_prime - new state after the action is performed
                reward: the reward gotten from taken action which resulted in state prime
                over: if the state_prime is the end of a sequence or not (ball at the end of the ramp)
        """
        #move the ball
        self.tick()

        #check if action is valid
        if self.check_valid_move(action):
            if action == 0: #STAY
                new_pos = self.goalie_pos
            elif action == 1: #LEFT
                new_pos = self.goalie_pos - 1
            elif action == 2: #RIGHT
                new_pos = self.goalie_pos + 1

            #update robot position
            self.update_goalie_pos(new_pos)

        #get state_prime based on type requsted
        if stateType == 'array':
            s = self.get_state_array()
        elif stateType == 'matrix':
            s = self.get_state_matrix()
        elif stateType == 'stacked':
            s = self.get_state_stacked(previous_state = previous_state)
        elif stateType == 'binary':
            s = self.get_state_binary(reshape_shape)

        reward = self.get_reward()
        over = self.is_done()
        
        #reset robot is at the end of the ramp
        if over:
            self.reset()

        return s, reward, over
        
    def is_done(self):
        """
            Whether it’s time to reset the environment again.
            This is used in experience replay for DQN
        
        """
        if self.gridworld:
            return self.ball_y == self.GRID_NUM_HEIGHT
        else:
            return self.ball_y >= (self.HEIGHT - self.ball_radius)


    def check_valid_move(self, action):
        """
            Check if requested action is within bounds of the enviornment

            Returns:
                True if valid, False if not
        """

        if self.goalie_pos == 0 and action == 1:
            return False
        elif self.goalie_pos == self.GRID_NUM_WIDTH-1 and action == 2:
            return False
        return True

    def get_reward(self):
        """
            Gets the reward of the current state of the enviornment

            Returns:
                1 if the robot caught the ball
                OR
                A negative number scalled to how close the robot was to the ball 
        """
       # print(self.ball_x,self.goalie_pos, self.ball_y, self.GRID_NUM_HEIGHT )
        if self.gridworld:
            if (self.ball_x == self.goalie_pos and self.ball_y == self.GRID_NUM_HEIGHT):
                return 1
            else:
                return -0.1 * (abs(self.goalie_pos - self.ball_x))
            #return 0
        else:
            #check if ball is within the x bounds of the robot
            #if center of ball plus radius is greater than the start of the robot
            # and
            # if the center of the ball minus the radius is less than the end of the robot
            if (((self.ball_x + self.ball_radius) >= (self.goalie_pos*self.GRID_SIZE)) and ((self.ball_x - self.ball_radius) <= (self.goalie_pos*self.GRID_SIZE + self.GRID_SIZE))):
                return 1
            else:
                #the 0,0 of the robot is the bottom left. To get the center of the robot it would be the bottom left plus one half of the size. The size of the robot is GRID_SIZE
                center_of_robot = self.goalie_pos*self.GRID_SIZE + ((1/2)*self.GRID_SIZE)
                # the 0,0 of the ball is the center of the ball
                center_of_ball = self.ball_x
                return -0.01 *(abs(center_of_robot - center_of_ball))

    def get_goalie_pos(self):
        return self.goalie_pos

    def ball_pos(self):
        return [self.ball_x, self.ball_y]

    def update_goalie_pos(self,new_pos):
        self.goalie_pos = new_pos
    
    def tick(self):
        if self.gridworld:
            self.ball_y = self.ball_y + 1
        else:
            self.ball_y += self.GRID_SIZE

    
   
        
    


        
        

