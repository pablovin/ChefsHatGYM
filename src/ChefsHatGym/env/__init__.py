from gym.envs.registration import register

register(
    id="chefshat-v1",
    entry_point="ChefsHatGym.env.ChefsHatEnv:ChefsHatEnv",
)
