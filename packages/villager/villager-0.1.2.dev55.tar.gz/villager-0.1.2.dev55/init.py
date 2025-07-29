# -*- coding: utf-8 -*-
from importlib.metadata import version


def motd():
    motd = r"""____   ____.__.__  .__                               
\   \ /   /|__|  | |  | _____     ____   ___________ 
 \   Y   / |  |  | |  | \__  \   / ___\_/ __ \_  __ \
  \     /  |  |  |_|  |__/ __ \_/ /_/  >  ___/|  | \/
   \___/   |__|____/____(____  /\___  / \___  >__|   
                             \//_____/      \/       """
    print(motd)
    try:
        __version__ = version("villager")
        print(f"当前版本: {__version__}")
    except Exception as e:
        print(f"无法获取版本信息: {e}")
        __version__ = "unknown"


def init():
    motd()
