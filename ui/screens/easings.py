from math import cos, sin, pi

# God bless https://easings.net

def clamp(value, lower, upper):
    return lower if value < lower else upper if value > upper else value

def ease_none(x):
    x = clamp(x, 0, 1)
    return x / 1

def ease_in_sine(x):
    x = clamp(x, 0, 1)
    return 1 - cos(x * pi / 2)

def ease_out_sine(x):
    x = clamp(x, 0, 1)
    return sin(x * pi / 2)

def ease_in_out_quad(x):
    x = clamp(x, 0, 1)
    return 2 * pow(x, 2) if x < 0.5 else 1 - pow(-2 * x + 2, 2) / 2

def ease_out_cubic(x):
    x = clamp(x, 0, 1)
    return 1 - pow(1 - x, 3)

def ease_in_out_cubic(x):
    x = clamp(x, 0, 1)
    return 4 * pow(x, 3) if x < 0.5 else 1 - pow(-2 * x + 2, 3) / 2

def ease_in_out_quart(x):
    x = clamp(x, 0, 1)
    return 8 * pow(x, 4) if x < 0.5 else 1 - pow(-2 * x + 2, 4) / 2

def ease_in_out_quint(x):
    x = clamp(x, 0, 1)
    return 16 * pow(x, 5) if x < 0.5 else 1 - pow(-2 * x + 2, 5) / 2

def ease_out_back(x):
    x = clamp(x, 0, 1)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * pow(x - 1, 3) + c1 * pow(x - 1, 2)

def ease_out_elastic(x):
    x = clamp(x, 0, 1)
    c = (2 * pi) / 3
    if x == 0:
        return 0
    elif x == 1:
        return 1
    else:
        return pow(2, -10 * x) * sin((x * 10 - 0.75) * c) + 1