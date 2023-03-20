import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation
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
rand_colors = [randHexColor() for i in range(100)]
y_coordinates = np.zeros(conveyor_length)

y_coordinates[11] = 1.2
x_offset = np.zeros(conveyor_length)
x_offset[11:] = -1

def update_conveyor_state(i):
    global conveyor_state_full
    global ix 
    conveyor_state = conveyor_state_full[ix]
    # Shift the conveyor belt by one position
   
    ax.clear()
    ax.set_xlim(-0.5, conveyor_length - 0.5)
    ax.set_ylim(-0.5, height - 0.5)
    ax.set_aspect('equal')
    ax.text(0, 10, f't={i}')
    ax.add_patch(plt.Rectangle((-0.5, -0.1), 10, 1.1, color = 'y')) 
    ax.add_patch(plt.Rectangle((9.5, -0.1), 1, 1.1, color = 'g')) 
    ax.add_patch(plt.Rectangle((10.5, -0.1), 5, 1.1, color = 'm')) 
                               
    #ax.plot(np.arange(conveyor_length), np.zeros((conveyor_length,)), 'k--')
    for j in range(conveyor_length):
        if conveyor_state[j] >= 1:
            ax.add_patch(plt.Rectangle((x_offset[j] + j - 0.5, y_coordinates[j]), 0.9, 0.9, color=rand_colors[int(conveyor_state[j])]))
            ax.text(x_offset[j] + j - 0.5 + 0.2, y_coordinates[j] + 0.2, f'{int(conveyor_state[j])}', color='k')

    ix += 1
    if ix >= len(conveyor_state_full):
        ix = 0
    return []

# Create the animation
fig, ax = plt.subplots()
anim= FuncAnimation(fig, update_conveyor_state, frames=np.arange(0, conveyor_state_full.shape[0]),
                          interval=conveyor_speed*1000, blit=True)
plt.show()

f = 'data/demo.gif' 
writergif = animation.PillowWriter(fps=2) 
anim.save(f, writer=writergif)

