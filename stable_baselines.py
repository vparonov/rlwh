from stable_baselines3.common.env_checker import check_env
from gym_env_adapter import WarehouseEnv

TRAINING_DIR = 'data/train_100_400_to_500_var'

env = WarehouseEnv('dqn_test', 'configurations/wh-stochastic.json', TRAINING_DIR, randomFileSelect=False)
# It will check your custom environment and output additional warnings if needed

check_env(env)