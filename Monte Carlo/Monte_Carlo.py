import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt
import pickle


def solve(train=True, render=False):
    env = gym.make('CartPole-v1', render_mode='human' if render else None)

    # Divide position, velocity, pole angle, and pole angular velocity into segments
    pos_space = np.linspace(-2.4, 2.4, 10)
    vel_space = np.linspace(-4, 4, 10)
    ang_space = np.linspace(-.2095, .2095, 10)
    ang_vel_space = np.linspace(-4, 4, 10)

    lr = 0.1  # alpha or learning rate
    d_factor = 0.99  # gamma or discount factor.

    eps = 1  # 1 = 100% random actions
    eps_decay = 0.00001  # epsilon decay rate
    rng = np.random.default_rng()  # random number generator

    rewards_per_episode = []

    if train:
        MC = np.zeros((len(pos_space) + 1,
                          len(vel_space) + 1,
                          len(ang_space) + 1,
                          len(ang_vel_space) + 1,
                          env.action_space.n))
    else:
        MC_SAVED = open('cartpole_monte_carlo.pkl', 'rb')
        MC = pickle.load(MC_SAVED)
        MC_SAVED.close()

    episodes = 100000
    for i in range(episodes):

        state = env.reset()[0]  # Starting position, starting velocity always 0
        state_p = np.digitize(state[0], pos_space)
        state_v = np.digitize(state[1], vel_space)
        state_a = np.digitize(state[2], ang_space)
        state_av = np.digitize(state[3], ang_vel_space)

        terminated = False  # True when reached goal

        rewards = 0

        while not terminated and rewards <= 200:

            if train and rng.random() < eps:
                # Choose random action  (0=go left, 1=go right)
                action = env.action_space.sample()
            else:
                action = np.argmax(MC[state_p, state_v, state_a, state_av, :])

            new_state, reward, terminated, _, _ = env.step(action)
            new_state_p = np.digitize(new_state[0], pos_space)
            new_state_v = np.digitize(new_state[1], vel_space)
            new_state_a = np.digitize(new_state[2], ang_space)
            new_state_av = np.digitize(new_state[3], ang_vel_space)

            if train and rng.random() < eps:
                # Choose random action  (0=go left, 1=go right)
                new_action = env.action_space.sample()
            else:
                new_action = np.argmax(MC[state_p, state_v, state_a, state_av, :])

            if train:
                MC[state_p, state_v, state_a, state_av, action] = \
                    MC[state_p, state_v, state_a, state_av, action] + \
                    lr * (reward +
                          d_factor * (
                              MC[new_state_p, new_state_v, new_state_a,
                              new_state_av, new_action]) - MC[
                              state_p, state_v, state_a, state_av, action]
                          )

            state = new_state
            action = new_action
            state_p = new_state_p
            state_v = new_state_v
            state_a = new_state_a
            state_av = new_state_av
            rewards += reward

        if not train:
            print(f'Episode: {i}  Rewards: {rewards}')

        rewards_per_episode.append(rewards)
        mean_rewards = np.mean(rewards_per_episode[len(rewards_per_episode) - 100:])

        if train and i % 100 == 0:
            print(f'Episode: {i} {rewards}  Epsilon: {eps:0.2f}  Mean Rewards {mean_rewards:0.1f}')
            with open("SARSA.txt", "a") as MC_SAVED:
                print(f'Episode: {i} {rewards}  Epsilon: {eps:0.2f}  Mean Rewards {mean_rewards:0.1f}',
                      file=MC_SAVED)

        if mean_rewards >= 195 and train:
            print(f'Episode: {i} {rewards}  Epsilon: {eps:0.2f}  Mean Rewards {mean_rewards:0.1f}')
            break

        eps = max(0, eps - eps_decay)

    env.close()

    # Save Monte Carlo table to file
    if train:
        MC_SAVED = open('cartpole_monte_carlo.pkl', 'wb')
        pickle.dump(MC, MC_SAVED)
        MC_SAVED.close()

    mean_rewards = []
    for t in range(i):
        mean_rewards.append(np.mean(rewards_per_episode[max(0, t - 100):(t + 1)]))
    plt.plot(mean_rewards)
    plt.savefig('cartpole_monte_carlo.png')


if __name__ == '__main__':
    # for training
    # solve(train=True, render=False)
    # for rendering
    solve(train=False, render=True)
