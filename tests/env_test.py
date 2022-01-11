import mathblocks
import gym
from mathblocks.blocks.constants import DIRECTION2STR
from mathblocks.oracles import DirectOracle
import time

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
        actn_times = {
            i: [0,0] for i in range(env.action_space.n)
        }
        step_times = [0,0]
        while step_times[1] < 5000:
            obs = env.reset()
            done = False
            while not done:
                print("Testing Env:", env_name)
                start_t = time.time()
                actn = oracle(env)
                actn_times[actn][0] += time.time()-start_t
                actn_times[actn][1] += 1
                print("Brain Time:", time.time()-start_t)
                if actn < 5:
                    print("actn:", DIRECTION2STR[actn])
                else:
                    print("actn: GRAB")
                start_t = time.time()
                obs, rew, done, info = env.step(actn)
                step_times[0] += time.time()-start_t
                step_times[1] += 1
                print("done: ", done)
                print("rew: ", rew)
                #env.render()
        for actn, tup in actn_times.items():
            if tup[1] == 0: tup[1] = 1
            if actn < 5: actn = DIRECTION2STR[actn]
            if actn == 5: actn = "GRAB"
            if actn == 6: actn = "DECOMP"
            print("action:", actn, "-- Avg Time:", tup[0]/tup[1])
        print("Step Time:", step_times[0]/step_times[1])

