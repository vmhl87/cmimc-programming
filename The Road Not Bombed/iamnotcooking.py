from math import exp, e, sqrt

control_points = [(0, 0), (4, 4), (15, 15), (8, 8), (12, 12)]
c = [1] * len(control_points)

def decay(dist):
    # return 1 / (dist + 1)
    return 1 / (dist ** 2 + 1)

def theta(x, y):
    p = 0
    for k, point in enumerate(control_points):
        p += c[k] * decay(sqrt((x - point[0]) ** 2 + (y - point[1]) ** 2))

    return p

def count(threshold):
    c = 0
    
    for y in range(16):
        for x in range(16):
            p = theta(x, y)
            bit = threshold(p)

            c += bit

    return c

def render(threshold):
    characters = [" ", "#"]
    
    for y in range(16):
        for x in range(16):
            p = theta(x, y)
            bit = threshold(p)
            print(characters[bit], end="")
            
        print()

def curry_threshold(value):
    return lambda p: p > value

def search(start, end):
    mid = (start + end) / 2

    c = count(curry_threshold(mid))
    N = 90

    if abs(c - N) <= 5:
        return mid
    elif c > N:
        return search(mid, end)
    else:
        return search(start, mid)

threshold_value = search(0, 1)
print(threshold_value)
print(count(curry_threshold(threshold_value)))

render(curry_threshold(threshold_value))
