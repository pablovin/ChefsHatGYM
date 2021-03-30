from gym.envs.registration import register

register(
    id='chefshat-v0',
    entry_point='ChefsHatGym.env.ChefsHatEnv:ChefsHatEnv',
)