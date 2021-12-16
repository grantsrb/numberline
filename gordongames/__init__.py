from gym.envs.registration import register

register(
    id='gordongames-v0',
    entry_point='gordongames.envs:EvenLineMatch',
)
register(
    id='gordongames-v1',
    entry_point='gordongames.envs:ClusterMatch',
)
#register(
#    id='gordongames-C',
#    entry_point='gordongames.envs:OrthoLineMatch',
#)
#register(
#    id='gordongames-D',
#    entry_point='gordongames.envs:UnevenLineMatch',
#)
#register(
#    id='gordongames-G',
#    entry_point='gordongames.envs:NutsInCan',
#)
#register(
#    id='gordongames-H',
#    entry_point='gordongames.envs:CandyInBox',
#)
