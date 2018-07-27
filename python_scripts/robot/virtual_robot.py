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

    def __init__(self,dpi, number_of_states_x,number_of_states_y,WIDTH,HEIGHT,roi_x,roi_y, initial_x,initial_y):
        
        self.dpi = dpi
        self.WIDTH =  WIDTH
        self.HEIGHT = HEIGHT

        self.screen_region_x = roi_x * self.dpi

        self.screen_region_y = roi_y * self.dpi
        self.number_of_states_x = number_of_states_x
        self.number_of_states_y = number_of_states_y

        self.offset_x = (self.WIDTH - self.screen_region_x) / 2.0
        self.offset_y = (self.HEIGHT - self.screen_region_y) / 2.0

        
        self.grid_position_x = initial_x
        self.grid_position_y = initial_y

        self.pixels_per_grid_x = self.screen_region_x / self.number_of_states_x
        self.pixels_per_grid_y = self.screen_region_y / self.number_of_states_y
    

        stddraw.setXscale(0, self.WIDTH)
        stddraw.setYscale(0, self.HEIGHT)
        stddraw.setCanvasSize(self.WIDTH,self.HEIGHT)


        #stddraw.filledRectangle(self.offset_x,self.offset_y,self.screen_region_x, self.screen_region_y) #x,y,size_x,size_y

    def drawRobot(self):
        #background
        stddraw.setPenColor(stddraw.BLACK)
        stddraw.filledRectangle(self.offset_x,self.offset_y,self.screen_region_x, self.screen_region_y) #x,y,size_x,size_y
        
        #robot
        stddraw.setPenColor(stddraw.RED)
        stddraw.filledRectangle(self.grid_position_x*self.pixels_per_grid_x+self.offset_x,
                                self.grid_position_y*self.pixels_per_grid_y+self.offset_y,
                                self.pixels_per_grid_x,
                                self.pixels_per_grid_y) #x,y,size_x,size_y
        
        stddraw.show(0)

    def get_goalie_pos(self):
        return self.grid_position_x, self.grid_position_y

    def update_position(self,action):
        if(action == 1):
            if(self.grid_position_x != 0):
                self.grid_position_x = self.grid_position_x - 1
        elif (action == 2):
            if(self.grid_position_x != self.number_of_states_x-1 ):
                self.grid_position_x = self.grid_position_x + 1
        elif (action == 3):
            if self.grid_position_y !=self.number_of_states_y - 1:
                self.grid_position_y = self.grid_position_y + 1
        elif action == 4:
            if self.grid_position_y != 0:
                self.grid_position_y = self.grid_position_y - 1

    def goToPosition(self,position_x,position_y):
        if ((position_x - 1) <= self.number_of_states_x) and ((position_y-1) <= self.number_of_states_y):
            self.grid_position_x = position_x - 1
            self.grid_position_y = position_y - 1
        
                

    
    