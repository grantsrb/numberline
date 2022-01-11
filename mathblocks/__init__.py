import gordongames.oracles
from gym.envs.registration import register

register(
    id='mathblocks-v0',
    entry_point='mathblocks.envs:MathBlocks',
)
