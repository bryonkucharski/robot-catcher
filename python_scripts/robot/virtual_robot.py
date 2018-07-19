'''
Bryon Kucharski, Adam Ziel, Mike Hickey, Collin Travers
Wentworth Institute of Technology
Summer 2018

stddraw princeton library to draw a 2D robot

'''

import os, sys, inspect
princeton_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../princeton_lib")))
if princeton_subfolder not in sys.path:
    sys.path.insert(0, princeton_subfolder)

import stddraw

#WIDTH = 1960
#HEIGHT = 1050
#dpi = 99
#ramp_length = 12.7953 #inches
#number_of_states = 5

#grid_size = ramp_length / number_of_states;
#grid_pixels = grid_size * dpi
#screen_region = grid_pixels * number_of_states
#offset = (WIDTH - screen_region) / 2

class virtual_robot:

    def __init__(self,ramp_length,robot_y_area,dpi, number_of_states_x,number_of_states_y,WIDTH,HEIGHT, initial_x,initial_y):
        
        self.dpi = dpi
        self.WIDTH =  WIDTH
        self.HEIGHT = HEIGHT

        self.ramp_length = ramp_length #inches
        self.robot_y_area = robot_y_area
        self.number_of_states_x = number_of_states_x
        self.number_of_states_y = number_of_states_y

        self.grid_size_x = self.ramp_length / self.number_of_states_x
        self.grid_pixels_x = self.grid_size_x * self.dpi

        self.grid_size_y = self.robot_y_area / self.number_of_states_y
        self.grid_pixels_y = self.grid_size_y * self.dpi

        self.screen_region_x =self.grid_pixels_x * self.number_of_states_x
        self.screen_region_y = self.grid_pixels_y * self.number_of_states_y

        self.offset_x = (self.WIDTH - self.screen_region_x) / 2
        self.offset_y = (self.HEIGHT - self.screen_region_y) / 2
        self.position_x = initial_x
        self.position_y = initial_y

        stddraw.setXscale(0, self.WIDTH)
        stddraw.setYscale(0, self.HEIGHT)
        stddraw.setCanvasSize(self.WIDTH,self.HEIGHT)


        stddraw.filledRectangle(self.offset_x,self.offset_y,self.screen_region_x, self.screen_region_y) #x,y,size_x,size_y

    def drawRobot(self):
        #background
        stddraw.setPenColor(stddraw.BLACK)
        stddraw.filledRectangle(self.offset_x,self.offset_y,self.screen_region_x, self.screen_region_y) #x,y,size_x,size_y

        #robot
        stddraw.setPenColor(stddraw.RED)
        stddraw.filledRectangle(self.position_x*self.grid_pixels_x+self.offset_x,
                                #self.position_y*(self.HEIGHT - self.grid_pixels),
                                self.position_y*self.grid_pixels_y+self.offset_y,
                                self.grid_pixels_x,
                                self.grid_pixels_y) #x,y,size_x,size_y
        stddraw.show(0)

    def get_goalie_pos(self):
        return self.position_x, self.position_y

    def update_position(self,action):
        if(action == 1):
            if(self.position_x != 0):
                self.position_x = self.position_x - 1
        elif (action == 2):
            if(self.position_x != self.number_of_states_x-1 ):
                self.position_x = self.position_x + 1
        elif (action == 3):
            if self.position_y != self.number_of_states_y - 1:
                self.position_y = self.position_y + 1
        elif action == 4:
            if self.position_y != 0:
                self.position_y = self.position_y - 1
                

    
    