import os, sys, inspect
import random
import time
from PIL import ImageGrab
import numpy as np
import matplotlib.pyplot as plt

#this is just to import rl agent from a different folder
rl_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../rl")))
if rl_subfolder not in sys.path:
    sys.path.insert(0, rl_subfolder)

from qlearning_agent import rl_agent

socket_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../socket")))
if socket_subfolder not in sys.path:
    sys.path.insert(0, socket_subfolder)

from tcp_server import tcp_socket


vision_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../vision")))
if vision_subfolder not in sys.path:
    sys.path.insert(0, vision_subfolder)

import discretize_vision as v

#RL constants
EPSILON =       1    # greedy police
ALPHA =         0.5     # learning rate
GAMMA =         1       # discount 


def wait_for_phrase(phrase):
    """
        Blocking call - reads socket until the data is the same as phrase "start", "stop", "test", etc.

        Args:
            phrase: The string to listen to over the socket
    """
    while(server.getData() != phrase):
        print("waiting for" + phrase )

def wait_for_number(num):
    """
        Blocking call - reads socket until the header is the same as num "0", "1", "2", etc.

        Args:
            num: The num to listen to over the socket

    """
    header = '-1'
    while header != num:
        data = server.getData().split(',')
        #print(data)
        header = data[0]
    return data


def get_state_vision(grid_dim):
    """
    Gets the state by cropping an image from the unity enviornment (hardcode crop for now)
    Then calls the vision functions to return the cell of the ball

    Args:
        A tuple of the grid dimensions. EX (5,8)
    
    Returns:
        The state as [robot_x, ball_x, ball_y ]
    """
    #hardcoded numbers, these will change
    screenImage = ImageGrab.grab(bbox=(305, 157, 580, 597))#(X, Y) starting position ; (W, H) ending position
    img = np.array(screenImage)#convert the image to a numpy array
    img_dim = img.shape[1], img.shape[0]
    cell_dim = v.get_cell_dimensions(img_dim, grid_dim)
    circle_center, radius = v.get_circle(img)
    cell = v.pixel_to_cell(circle_center, cell_dim)
    
    #print(cell)
    robot_x = get_robot_pos()
    if(len(cell) == 0):
        return ([-1000,-1000], -1000)
    else:
        return ([ robot_x, int(cell[0]) ], int(cell[1]))
    

def get_robot_pos():
    """
    Sends the number 3 over the socket
    Unity is waiting for the number 3 and will return the robot position

    NOTE: Prob dont need to do this and can use vision instead

    Returns:
        The robot position from Unity
    """
    server.sendData('3')
    header = '-1'
    data = wait_for_number('3')

    #ball_y = float(data[3])
    robot_x = int(data[1])

    return robot_x

   
def get_state_unity():
    """
    requst data from unity
    wait until socket header is 0
    parse data
    """

    server.sendData('0')
    header = '-1'
    data = wait_for_number('0')

    ball_x = float(data[2])
    robot = int(data[1])
    return [robot, ball_x]


def send_action(a):
    """
    Sends the string over a socket in the form of '1,action'
    To move left, it would be the string '1,1'
    Unity is checking for the header to be 1
    """

    server.sendData('1,' + str(a))
    wait_for_number('1')

def get_reward():
    """
    Sends the number 2 over the socket
    Unity is waiting for the number 2 and will return the reward

    Returns:
        The reward from Unity
    """
    server.sendData('2')
    data = wait_for_number('2')
    reward = float(data[1])
    #print(reward)
    return reward

#def calculateReward():
    

agent = rl_agent(
                list(range(3)), #STAY,LEFT,RIGHT
                GAMMA,
                ALPHA,
                EPSILON
               )
           
server = tcp_socket(
                    host = '',
                    port = 50000, 
                    backlog = 5, #amount of requests to queue at one time
                    size = 1024 
                    )

agent.init_q_table()
#agent.init_stddraw(500)

i = 0
epochs = 1000
update_rate = 1/5
grid_dim = (5,10)



start = time.time()
test = time.time()


wait_for_phrase("start")

iters = 0
num_catches = 0
total_reward = 0
total_rewards = []
num_epochs = []


while(i < epochs):

    end = time.time()
    elapsed = end - start

   # if(elapsed > update_rate):
    start = time.time()

    ####Get the State####
    #(state, ball_y) = get_state_vision(grid_dim)
    state = get_state_unity()

    ####Get the Action####
    action = agent.get_action(str(state))
    
    #Perform the action by sending a command to Unity
    send_action(action)
    
    ####Get the Reward from Unity####
    reward = get_reward()
    total_reward = total_reward + reward

    ####Get the State Prime####
    #state_prime, ball_y = get_state_vision(grid_dim)
    state_prime = get_state_unity()

    #print(str(state) + ", " + str(action) + ", " + str(reward) + ", " + str(state_prime))
    agent.update(str(state),action,reward,str(state_prime))

    if (i % 10 == 0):
        total_rewards.append(total_reward)
        num_epochs.append(i)
    #    os.system('cls')
        #agent.print_q_table()
    #agent.visualize_q_table(500)


    i = i + 1
    
print(total_rewards)
print(num_epochs)
plt.plot(num_epochs,total_rewards)
plt.title("Cumulative Reward in 3D Simulation")
plt.ylabel("Cumulative Reward")
plt.xlabel("Number of Updates")
plt.show()
agent.print_q_table()

