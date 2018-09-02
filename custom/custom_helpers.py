#coding=utf-8

import numpy as np
import random

from constants import *
from mobject.types.vectorized_mobject import VGroup
from utils.color import rgb_to_color, color_to_rgb


def list_shuffle(l):
    """Return a shuffled copy of the original list ``l``."""
    x = l[:]
    random.shuffle(x)
    return x

def vgroup_expansion(mobs):
    """Flatten a nested VGroup object ``mobs``."""
    while any(map(lambda x: isinstance(x, VGroup), mobs)):
        expanded_mobs = []
        for mob in mobs.submobjects:
            expanded_mobs.extend(mob)
        mobs = VGroup(expanded_mobs)
    return mobs

def mobs_shuffle(mobs):
    """Shuffle the submobjects inside a VGroup object ``mobs``."""
    mobs = vgroup_expansion(mobs)
    mobs.submobjects = list_shuffle(mobs.submobjects)
    return mobs

def tweak_color(color1, color2, weight = 0.3):
    """Return a weighted-average of two colors."""
    weight = np.clip(weight, 0, 1)
    tweaked_rgb = weight * color_to_rgb(color2) + (1-weight) * color_to_rgb(color1)
    return rgb_to_color(tweaked_rgb)

def brighten(color, weight = 0.3):
    return tweak_color(color, WHITE, weight)

def darken(color, weight = 0.3):
    return tweak_color(color, BLACK, weight)



