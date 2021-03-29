from gym.envs.registration import register

register(
    id='chefshat-v0',
    entry_point='env.ChefsHatEnv:ChefsHatEnv',
)