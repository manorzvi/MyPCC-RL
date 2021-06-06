import gym
import gym_aurora
import gym_myaurora

if __name__ == '__main__':
    env = gym.make('PCC-Aurora-v1', history_len=5)
    for i_episode in range(5):
        observation = env.reset()
        for t in range(10):
            print(observation)
            action = env.action_space.sample()
            observation, reward, done, info = env.step(action)
            if done:
                print("Episode finished after {} timesteps".format(t+1))
                break
    env.close()


