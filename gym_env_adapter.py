from warehouse import Warehouse

import  gym
import numpy as np
from gym import spaces


class WarehouseEnv(gym.Env):

    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self,  name, fileName, datadir, randomFileSelect):
        super(WarehouseEnv).__init__()
        self.warehouse = Warehouse(name, fileName, datadir, randomFileSelect)
        self.action_space = spaces.Discrete(self.warehouse.action_space.n)

        state, _,_ = self.warehouse.reset()
        n_observations = len(state) - 2

        self.observation_space = spaces.Box(low=0, high=1.0,
                                        shape=(n_observations,), dtype=np.float32)

    def step(self, action):
        observation, reward, terminated, truncated, (info, _, _, _) = self.warehouse.step(action)
        done = terminated or truncated
        return observation[1:-1], reward, done, {}

    def reset(self, seed=None, options=None):
        observation, _,_ = self.warehouse.reset()
        return observation[1:-1]

    def render(self):
        pass

    def close(self):
        pass