import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib
import numpy as np
import matplotlib.patches as mpatches
import sys


style.use('fivethirtyeight')

q_table_file = sys.argv[1]
network_file = sys.argv[2]


q_t = open(q_table_file,'r').read()
nw = open(network_file,'r').read()

qt_lines = q_t.split("\n")
nw_lines = nw.split("\n")

epochs = []
nw_reward = []
nw_catches = []
qt_catches = []
qt_reward = []


for qt_line,nw_line in zip(qt_lines,nw_lines):
    if len(qt_line) > 1 and len(nw_line) > 1:
        
        
        epoch,qt_avg_reward,qt_avg_catches = qt_line.split(',')
        epoch,nw_avg_reward,nw_avg_catches = nw_line.split(',')
        epoch = int(epoch)

        qt_avg_reward = float(qt_avg_reward)
        qt_avg_catches = float(qt_avg_catches) * 100

        nw_avg_reward = float(nw_avg_reward)
        nw_avg_catches = float(nw_avg_catches) * 100

        epochs.append(epoch)

        nw_catches.append(nw_avg_catches)
        nw_reward.append(nw_avg_reward)

        qt_catches.append(qt_avg_catches)
        qt_reward.append(qt_avg_reward)

fontsize=32

plt.figure(1)
plt.plot(epochs,nw_reward, color = 'red')
plt.plot(epochs,qt_reward, color = 'blue')
plt.title("10 x 10 Q-Table vs DQN: Average Cumulative Reward", fontsize=fontsize )
plt.ylabel("Cumulative Reward", fontsize=fontsize)
plt.xlabel("Number of Ball Rolls", fontsize=fontsize)
nw_patch = mpatches.Patch(color='red', label='DQN')
qt_patch = mpatches.Patch(color='blue', label='Q-Table')
plt.legend(handles=[nw_patch,qt_patch])

plt.show()

plt.figure(1)
plt.plot(epochs,nw_catches, color = 'red')
plt.plot(epochs,qt_catches, color = 'blue')
plt.title("10 x 10 Q-Table vs DQN: Average Accuracy ", fontsize=fontsize)
plt.ylabel("Average Accuracy (Perecentage)", fontsize=fontsize)
plt.xlabel("Number of Ball Rolls", fontsize=fontsize)
nw_patch = mpatches.Patch(color='red', label='DQN')
qt_patch = mpatches.Patch(color='blue', label='Q-Table')
plt.legend(handles=[nw_patch,qt_patch])
plt.show()
