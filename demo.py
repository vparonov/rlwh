import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random 

def randHexColor():
        return '#{:02X}{:02X}{:02X}'.format(random.randint(50, 200),random.randint(50, 200),random.randint(50, 200))
    
# Define the dimensions of the warehouse
width = 10
height = 10

# Define the parameters of the conveyor belt
conveyor_length = 17
conveyor_speed = 0.5

conveyor_state_full = np.load('data/states.npy')
ix = 0

def update_conveyor_state(i):
    global conveyor_state_full
    global ix 
    conveyor_state = conveyor_state_full[ix]
    # Shift the conveyor belt by one position
   
    ax.clear()
    ax.set_xlim(-0.5, conveyor_length - 0.5)
    ax.set_ylim(-0.5, height - 0.5)
    ax.set_aspect('equal')
    ax.plot(np.arange(conveyor_length), np.zeros((conveyor_length,)), 'k--')
    for j in range(conveyor_length):
        if conveyor_state[j] == 1:
            ax.add_patch(plt.Rectangle((j - 0.5, 0), 0.9, 0.9, color='blue'))

    ix += 1
    if ix >= len(conveyor_state_full):
        ix = 0
    return []

# Create the animation
fig, ax = plt.subplots()
animation = FuncAnimation(fig, update_conveyor_state, frames=np.arange(0, 100),
                          interval=conveyor_speed*1000, blit=True)
plt.show()


