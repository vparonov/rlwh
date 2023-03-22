import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import numpy as np 
import torch 

def plot(title, npstate, sorted_components):
    figure(figsize=(8, 6), dpi=80)
    cmap = plt.cm.inferno 
    _, ax = plt.subplots(1,1)
    img = ax.imshow(npstate.T, aspect= 'auto', cmap=cmap, interpolation='nearest')
    ax.set_yticks(range(len(sorted_components)))
    ax.set_yticklabels(sorted_components)
    plt.xlabel('time step')
    plt.ylabel('component')
    plt.title(title, fontsize = 8)
    plt.colorbar(img)
    plt.savefig(f'fig/{title}.png')
    #plt.show()


def saveModel(model, file_name):    
    torch.save(model.state_dict(), file_name)

def loadModel(model, file_name):
    model.load_state_dict(torch.load(file_name))
    model.eval()
    return model