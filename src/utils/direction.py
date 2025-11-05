UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

ALL_DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

DIRECTION_DELTAS = {
    UP: (0, -1),
    DOWN: (0, 1),
    LEFT: (-1, 0),
    RIGHT: (1, 0)
}

def get_delta(direction):
    return DIRECTION_DELTAS.get(direction, (0, 0))

def apply_direction(x, y, direction):
    dx, dy = get_delta(direction)
    return x + dx, y + dy
