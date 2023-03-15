import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Define the dimensions of the warehouse
width = 10
height = 10

# Define the parameters of the conveyor belt
conveyor_length = 20
conveyor_speed = 0.5

# Define the initial state of the conveyor belt
conveyor_state = np.zeros((conveyor_length,), dtype=int)
conveyor_state[0] = 1  # set the first position to occupied

# Define a function to update the state of the conveyor belt
def update_conveyor_state(i):
    global conveyor_state
    # Shift the conveyor belt by one position
    conveyor_state[1:] = conveyor_state[:-1]
    conveyor_state[0] = 0  # set the first position to unoccupied
    # Generate new items with a probability of 0.2
    if np.random.rand() < 0.2:
        conveyor_state[0] = 1
    # Update the plot
    ax.clear()
    ax.set_xlim(-0.5, conveyor_length - 0.5)
    ax.set_ylim(-0.5, height - 0.5)
    ax.set_aspect('equal')
    ax.plot(np.arange(conveyor_length), np.zeros((conveyor_length,)), 'k--')
    for j in range(conveyor_length):
        if conveyor_state[j] == 1:
            ax.add_patch(plt.Rectangle((j - 0.5, 0), 1, 1, color='blue'))
    return []

# Create the animation
fig, ax = plt.subplots()
animation = FuncAnimation(fig, update_conveyor_state, frames=np.arange(0, 100),
                          interval=conveyor_speed*1000, blit=True)
plt.show()
