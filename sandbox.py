import torch 
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

n_time_steps = 10 
n_observations = 17
output_features = 2

hidden_size = 128
batch_size = 32
n_lstm_layers = 1


# state = torch.zeros(n_time_steps, n_observations)

# for i in range(20):
#     state_step = i * torch.ones(n_observations)
#     state = torch.roll(state, -1, 0)
#     state[-1] = state_step
#     print(state)

# inp = torch.randn(batch_size, n_time_steps, n_observations)

# layer1 = nn.Linear(in_features= n_observations, out_features = hidden_size)

# lstm_layer = nn.LSTM(input_size = hidden_size, hidden_size = hidden_size, batch_first = True)

# layer2 = nn.Linear(in_features = hidden_size, out_features = output_features)


# hidden_state = torch.randn(n_lstm_layers, batch_size, hidden_size)
# cell_state = torch.randn(n_lstm_layers, batch_size, hidden_size)

# hidden = (hidden_state, cell_state)

# x = layer1(inp)
# out, hidden = lstm_layer(x, hidden)
# print(out.shape)
# out = out[:, -1, :]
# print(out.shape)
# out = layer2(out)
# print(out.shape)


normalizedState =  np.zeros((10, 19-2-10+2))
normalizedState[-1] = np.ones(19-2-10+2)
normalizedState = np.roll(normalizedState, -1, 0)
print(normalizedState)
state = torch.tensor(normalizedState, dtype=torch.float32, device='cpu').unsqueeze(0)

print(state.shape)