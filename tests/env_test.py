import mathblocks
import gym
from mathblocks.blocks.constants import DIRECTION2STR
from mathblocks.oracles import DirectOracle

if __name__=="__main__":
    kwargs = {
        "targ_range": (1,25),
        "grid_size": (50,30),
        "pixel_density": 1,
        "max_num": 50
    }
    env_names = [
        "mathblocks-v0",
    ]
    for env_name in env_names:
        print("Testing Env:", env_name)
        for k,v in kwargs.items():
            print(k, "-", v)
        env = gym.make(env_name, **kwargs)
        oracle = DirectOracle(env_name)
        for i in range(7):
            obs = env.reset()
            done = False
            while not done:
                print("Testing Env:", env_name)
                actn = oracle(env)
                if actn < 5:
                    print("actn:", DIRECTION2STR[actn])
                else:
                    print("actn: GRAB")
                obs, rew, done, info = env.step(actn)
                print("done: ", done)
                print("rew: ", rew)
                env.render()

