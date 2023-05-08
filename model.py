
import torch.nn as nn
import torch.nn.functional as F
import torch 

class DQN(nn.Module):
    def __init__(self, n_observations, n_actions):
        super(DQN, self).__init__()
        self.layer1 = nn.Linear(n_observations, 128)
        self.layer2 = nn.Linear(128, 128)
        self.layer3 = nn.Linear(128, n_actions)

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        return self.layer3(x)


class DQN_LSTM(nn.Module):
    def __init__(self, n_observations, n_actions, hidden_size = 128): 
        super(DQN_LSTM, self).__init__()
        self.hidden_size = hidden_size
        self.input_layer = nn.Linear(in_features= n_observations, out_features = hidden_size)
        self.lstm_layer = nn.LSTM(input_size = hidden_size, hidden_size = hidden_size, batch_first = True)
        self.output_layer = nn.Linear(in_features = hidden_size, out_features = n_actions)

    def forward(self, x):
        batch_size = x.shape[0]
        x = F.relu(self.input_layer(x))

        hidden_state = torch.randn(1, batch_size, self.hidden_size)
        cell_state = torch.randn(1, batch_size, self.hidden_size)
        hidden = (hidden_state, cell_state)

        out, hidden = self.lstm_layer(x, hidden)
        out = out[:, -1, :]
        return self.output_layer(out)

class DQN256(nn.Module):
    def __init__(self, n_observations, n_actions):
        super(DQN256, self).__init__()
        self.layer1 = nn.Linear(n_observations, 256)
        self.layer2 = nn.Linear(256, 256)
        self.layer3 = nn.Linear(256, n_actions)

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        return self.layer3(x)

class DQN64(nn.Module):
    def __init__(self, n_observations, n_actions):
        super(DQN64, self).__init__()
        self.layer1 = nn.Linear(n_observations, 64)
        self.layer2 = nn.Linear(64, 64)
        self.layer3 = nn.Linear(64, n_actions)

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        return self.layer3(x)

class DQN64_64(nn.Module):
    def __init__(self, n_observations, n_actions):
        super(DQN64_64, self).__init__()
        self.layer1 = nn.Linear(n_observations, 64)
        self.layer21 = nn.Linear(64, 64)
        self.layer22 = nn.Linear(64, 64)
        self.layer3 = nn.Linear(64, n_actions)

    def forward(self, x):
        x = F.elu(self.layer1(x))
        x = F.elu(self.layer21(x))
        x = F.elu(self.layer22(x))
        return self.layer3(x)

class DQN128_128(nn.Module):
    def __init__(self, n_observations, n_actions):
        super(DQN128_128, self).__init__()
        self.layer1 = nn.Linear(n_observations, 128)
        self.layer21 = nn.Linear(128, 128)
        self.layer22 = nn.Linear(128, 128)
        self.layer3 = nn.Linear(128, n_actions)

    def forward(self, x):
        x = F.elu(self.layer1(x))
        x = F.elu(self.layer21(x))
        x = F.elu(self.layer22(x))
        return self.layer3(x)
