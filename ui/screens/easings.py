from math import cos, sin, pi

# God bless https://easings.net

def clamp(value, lower, upper):
    return lower if value < lower else upper if value > upper else value

def ease_in_sine(x):
    x = clamp(x, 0, 1)
    return 1 - cos(x * pi / 2)

def ease_out_elastic(x):
    x = clamp(x, 0, 1)
    c = (2 * pi) / 3
    if x == 0:
        return 0
    elif x == 1:
        return 1
    else:
        return pow(2, -10 * x) * sin((x * 10 - 0.75) * c) + 1