from math import cos, pi

# God bless https://easings.net

def ease_in_sine(x):
    # x = clamp(0, 1, x)
    return 1 - cos(x * pi / 2)