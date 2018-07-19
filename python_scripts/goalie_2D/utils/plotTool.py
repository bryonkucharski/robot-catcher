import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

style.use('fivethirtyeight')

fig  = plt.figure()
ax1 = fig.add_subplot(1,1,1)

def animate(i):
    data = open('plot_combined.txt','r').read()
    lines = data.split("\n")
    epochs = []
    total = []
    r_x = []
    r_y = []

    for line in lines:
        if len(line) > 1:
            #epoch,total_reward = line.split(',')
            epoch,total_reward, reward_x, reward_y = line.split(',')
            epoch = int(epoch)
            total_reward = float(total_reward)
            reward_x = float(reward_x)
            reward_y = float(reward_y)
            epochs.append(epoch)
            total.append(total_reward)
            r_x.append(reward_x)
            r_y.append(reward_y)

    ax1.clear()
    ax1.plot(epochs,total, color = 'r')
    ax1.plot(epochs,r_x, color = 'g')
    ax1.plot(epochs,r_y, color = 'b')

ani = animation.FuncAnimation(fig,animate,interval=1000)
plt.show()