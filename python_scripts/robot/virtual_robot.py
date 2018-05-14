import os, sys, inspect

#this is just to import stddraw from a different folder
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

    def __init__(self,ramp_length,dpi, number_of_states,WIDTH,HEIGHT):
        
        self.dpi = dpi
        self.ramp_length = ramp_length #inches
        self.number_of_states = number_of_states
        self.grid_size = self.ramp_length / self.number_of_states
        self.grid_pixels = self.grid_size * dpi
        self.screen_region =self.grid_pixels * self.number_of_states
        self.WIDTH =  WIDTH
        self.HEIGHT = HEIGHT
        self.offset = (self.WIDTH - self.screen_region) / 2
    
        self.position = 0

        stddraw.setXscale(0, self.WIDTH)
        stddraw.setYscale(0, self.HEIGHT)
        stddraw.setCanvasSize(self.WIDTH,self.HEIGHT)
        stddraw.filledRectangle(self.offset,0,self.screen_region, self.HEIGHT) #x,y,size_x,size_y

    def drawRobot(self):
        stddraw.setPenColor(stddraw.BLACK)
        stddraw.filledRectangle(self.offset,0,self.screen_region, self.HEIGHT) #x,y,size_x,size_y
        stddraw.setPenColor(stddraw.RED)
        stddraw.filledRectangle(self.position*self.grid_pixels+self.offset,
                                self.HEIGHT - self.grid_pixels,
                                self.grid_pixels,
                                self.grid_pixels) #x,y,size_x,size_y
        stddraw.show(0)

    def get_pos(self):
        return self.position

    def update_position(self,action):
        if(action == 1):
            if(self.position != 0):
                self.position = self.position - 1
        elif (action == 2):
            if(self.position != self.number_of_states-1 ):
                self.position = self.position + 1

    