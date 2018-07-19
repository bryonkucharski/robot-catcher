import math 

class kinematics:
    
    def __init__(self, theta, v_init, a):
        self.theta = theta
        self.v_init = v_init
        self.a = a

        self.v_init_x = self.v_init * math.cos(math.radians(self.theta))
        
        self.v_init_y = self.v_init * math.sin(math.radians(self.theta))

    def distance(self, time):

        dx = self.v_init_x * time
        dy = (self.v_init_y * time) + ((1/2) * self.a * (time*time))

        return dx, dy

    def determine__x(self, y_to_use):
        '''
        Determine what distance x will be at given distance y
        '''
     
        time = 2*self.v_init_y / (y_to_use - self.a)

        dx,dy = self.distance(time)

        print('Determine landing at time ' + str(time) + ' at x = '  + str(dx))

        return dx

    def distance_2(self, v_final, time):
        v_final_x = v_final * math.cos(self.theta)
        v_final_y = v_final * math.sin(self.theta)

        dx =( (self.v_init_x + v_final_x) /2 ) * time
        dy = None

        return dx, dy
    
    def v_final(self, dy):
        
        vfx = self.v_init_x
        vfy = math.sqrt(  (self.v_init_x * self.v_init_x) + (2 * self.a * dy)  )

        return vfx, vfy

    def v_final_2(self, time):
        
        vfx = self.v_init_x
        vfy = v_init_y + (self.a * time)
        
        return vfx, vfy


