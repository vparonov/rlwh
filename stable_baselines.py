from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import PPO, A2C, DQN
from gym_env_adapter import WarehouseEnv

TRAINING_DIR = 'data/train_100_400_to_500_var'

env = WarehouseEnv('dqn_test', 'configurations/wh-stochastic.json', TRAINING_DIR, randomFileSelect=False)
# It will check your custom environment and output additional warnings if needed

check_env(env)

model = DQN("MlpPolicy", env, verbose=1, batch_size=256, tau=0.001).learn(1000*600)

obs = env.reset()
n_steps = 500
for step in range(n_steps):
    action, _ = model.predict(obs, deterministic=True)
    print(f"Step {step + 1}")
    print("Action: ", action)
    obs, reward, done, info = env.step(action)
    print("obs=", obs, "reward=", reward, "done=", done)
    env.render()
    if done:
        # Note that the VecEnv resets automatically
        # when a done signal is encountered
        print("Goal reached!", "reward=", reward)
        break