from gym.envs.registration import register

register(
    id='PCC-MyAurora-v0',
    entry_point='gym_myaurora.envs:MyAuroraEnv',
)