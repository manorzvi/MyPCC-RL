from gym.envs.registration import register

register(
    id='PCC-Aurora-v0',
    entry_point='gym_aurora.envs:AuroraEnv',
)

register(
    id='PCC-Aurora-v1',
    entry_point='gym_aurora.envs:MultiSenderAuroraEnv',
)
