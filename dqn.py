# based on https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html
import os

os.environ['KMP_DUPLICATE_LIB_OK']='True'

import math
import random
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from collections import namedtuple, deque
from itertools import count

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F


from warehouse import Warehouse
from model import DQN, DQN64, DQN64_64, DQN256, DQN128_128
from utils import saveModel
from onnxutils import saveModelToOnnx


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward'))


class ReplayMemory(object):
    def __init__(self, capacity):
        self.memory = deque([],maxlen=capacity)

    def push(self, *args):
        """Save a transition"""
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)




# BATCH_SIZE is the number of transitions sampled from the replay buffer
# GAMMA is the discount factor as mentioned in the previous section
# EPS_START is the starting value of epsilon
# EPS_END is the final value of epsilon
# EPS_DECAY controls the rate of exponential decay of epsilon, higher means a slower decay
# TAU is the update rate of the target network
# LR is the learning rate of the AdamW optimizer

# best hyper parameters
# BATCH_SIZE = 512
# GAMMA = 0.99
# EPS_START = 0.9
# EPS_END = 0.05
# EPS_DECAY = 1000
# TAU = 0.05
# LR = 1e-4
# num_episodes = 1000
# # +alpha = 0.80
#TRAINING_DIR = 'data/train_100_400_to_500_var'
#reward function => return alpha * (countReceived / self.t) + (1.0-alpha) * (countReceived / self.nitems)


# second best  
# BATCH_SIZE = 512
# GAMMA = 0.99
# EPS_START = 0.9
# EPS_END = 0.05
# EPS_DECAY = 1000
# TAU = 0.05
# LR = 1e-4
# num_episodes = 1000
# # +alpha = 0.80
# # + new reward function
# TRAINING_DIR = 'data/train_100_400_to_500_var'
#memory = ReplayMemory(20000)



BATCH_SIZE = 256
GAMMA = 0.9999
EPS_START = 0.99   
EPS_END = 0.01
EPS_DECAY = 100000
TAU = 0.001
LR = 1e-4
num_episodes = 2000
memory = ReplayMemory(200000)


TRAINING_DIR = 'data/train_100_400_to_500_var'

env = Warehouse('dqn_test', 'configurations/wh-stochastic.json', TRAINING_DIR, randomFileSelect=False)

# Get number of actions from gym action space
n_actions = env.action_space.n

#reset without parameters randomly picks some of the files in data/train to load the items
state, _,_ = env.reset()

n_observations = len(state) - 2

# best policy_net = DQN(n_observations, n_actions).to(device)
# best target_net = DQN(n_observations, n_actions).to(device)

policy_net = DQN(n_observations, n_actions).to(device)
target_net = DQN(n_observations, n_actions).to(device)
target_net.load_state_dict(policy_net.state_dict())

optimizer = optim.AdamW(policy_net.parameters(), lr=LR, amsgrad=True)

steps_done = 0

def select_action(state, actions_mask):
    global steps_done
    sample = random.random()
    eps_threshold = EPS_END + (EPS_START - EPS_END) * \
        math.exp(-1. * steps_done / EPS_DECAY)
    steps_done += 1
    if sample > eps_threshold:
        with torch.no_grad():
            # t.max(1) will return largest column value of each row.
            # second column on max result is index of where max element was
            # found, so we pick action with the larger expected reward.
            return policy_net(state).max(1)[1].view(1, 1)
    else:
        return torch.tensor([[env.action_space.sample()]], device=device, dtype=torch.long)

episode_rewards = []
loss_log = [] 

def plot_rewards(show_result=False):
    plt.figure(1)
    rewards_t = torch.tensor(episode_rewards, dtype=torch.float)
    if show_result:
        plt.title(f'Result {TRAINING_DIR}')
    else:
        plt.clf()
        plt.title(f'Training...{TRAINING_DIR}')
    plt.xlabel('Episode')
    plt.ylabel('Reward')
    plt.plot(rewards_t.numpy())
    # Take 100 episode averages and plot them too
    if len(rewards_t) >= 100:
        means = rewards_t.unfold(0, 100, 1).mean(1).view(-1)
        means = torch.cat((torch.zeros(99), means))
        plt.plot(means.numpy())

    plt.pause(0.001)  # pause a bit so that plots are updated

def optimize_model():
    if len(memory) < BATCH_SIZE:
        return
    transitions = memory.sample(BATCH_SIZE)
    # Transpose the batch (see https://stackoverflow.com/a/19343/3343043 for
    # detailed explanation). This converts batch-array of Transitions
    # to Transition of batch-arrays.
    batch = Transition(*zip(*transitions))

    # Compute a mask of non-final states and concatenate the batch elements
    # (a final state would've been the one after which simulation ended)
    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                          batch.next_state)), device=device, dtype=torch.bool)
    non_final_next_states = torch.cat([s for s in batch.next_state
                                                if s is not None])
    state_batch = torch.cat(batch.state)
    action_batch = torch.cat(batch.action)
    reward_batch = torch.cat(batch.reward)

    # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
    # columns of actions taken. These are the actions which would've been taken
    # for each batch state according to policy_net
    state_action_values = policy_net(state_batch).gather(1, action_batch)

    # Compute V(s_{t+1}) for all next states.
    # Expected values of actions for non_final_next_states are computed based
    # on the "older" target_net; selecting their best reward with max(1)[0].
    # This is merged based on the mask, such that we'll have either the expected
    # state value or 0 in case the state was final.
    next_state_values = torch.zeros(BATCH_SIZE, device=device)
    with torch.no_grad():
        next_state_values[non_final_mask] = target_net(non_final_next_states).max(1)[0]
    # Compute the expected Q values
    expected_state_action_values = (next_state_values * GAMMA) + reward_batch

    # original # Compute Huber loss
    #criterion = nn.SmoothL1Loss()
    criterion = nn.MSELoss()
    loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1).float())

    # Optimize the model
    optimizer.zero_grad()
    loss.backward()

    loss_log.append(loss.item())
    # In-place gradient clipping
    torch.nn.utils.clip_grad_value_(policy_net.parameters(), 100)
    optimizer.step()


global_t = 0 

for i_episode in range(num_episodes):
    # Initialize the environment and get it's state
    # if i_episode == 500:
    #     print('switch to the stochastic picker''s env')
    #     env = Warehouse('dqn_test', 'files/wh1.txt', TRAINING_DIR, randomFileSelect=False)

    state, _, actions_mask = env.reset()
    # the sink component's capacity = the number of items
    normalizedState =  np.zeros(len(state)-2)

    state = torch.tensor(normalizedState, dtype=torch.float32, device=device).unsqueeze(0)

    for t in count():
        action = select_action(state, actions_mask)
        observation, reward, terminated, truncated, (info, nitems, actions_mask, _) = env.step(action.item())
        reward = torch.tensor([reward], device=device)
        done = terminated or truncated

        if truncated:
            print(f'failed: {info}')
        if terminated:
            next_state = None
        else:
            # exclude source and sink components 
            normalizedState = observation[1:-1]
            next_state = torch.tensor(normalizedState, dtype=torch.float32, device=device).unsqueeze(0)

        # Store the transition in memory
        memory.push(state, action, next_state, reward)

        # Move to the next state
        state = next_state

        # Perform one step of the optimization (on the policy network)
        optimize_model()

        # Soft update of the target network's weights
        # θ′ ← τ θ + (1 −τ )θ′
        target_net_state_dict = target_net.state_dict()
        policy_net_state_dict = policy_net.state_dict()

        # if global_t%2000 == 0:
        #     print(f' {t} copy policy to target net')
        #     for key in policy_net_state_dict:
        #         target_net_state_dict[key] = policy_net_state_dict[key]
        #     target_net.load_state_dict(target_net_state_dict)
    
        for key in policy_net_state_dict:
            target_net_state_dict[key] = policy_net_state_dict[key]*TAU + target_net_state_dict[key]*(1-TAU)
        target_net.load_state_dict(target_net_state_dict)
        global_t+=1
        if done:
            episode_rewards.append(reward)
            plot_rewards()
            break
    if i_episode % 100 == 0:
        saveModelToOnnx(policy_net, n_observations, f'models/trained_policy_network_{i_episode}.onnx')
        saveModel(policy_net, f'models/trained_policy_network_{i_episode}.pt')
        saveModelToOnnx(target_net, n_observations, f'models/trained_target_policy_network_{i_episode}.onnx')
        saveModel(target_net, f'models/trained_target_policy_network_{i_episode}.pt')

print('Complete')

#saveModelToOnnx(target_net, n_observations, 'models/trained_policy_network.onnx')
#saveModel(target_net, 'models/trained_policy_network.pt')

saveModelToOnnx(policy_net, n_observations, 'models/trained_policy_network.onnx')
saveModel(policy_net, 'models/trained_policy_network.pt')
saveModelToOnnx(target_net, n_observations, 'models/trained_target_policy_network.onnx')
saveModel(target_net, 'models/trained_target_policy_network.pt')

plot_rewards(show_result=True)
plt.ioff()
plt.show()

plt.plot(loss_log)
plt.xlabel('Episode')
plt.ylabel('Loss')
plt.show()
