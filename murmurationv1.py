import random
import math
import curses
import time

# Console setup
width, height = 160, 60

# Create starlings
num_starlings = 300
starlings = []

for _ in range(num_starlings):
    starling = {'x': random.randint(0, width), 'y': random.randint(0, height),
                'dx': random.uniform(-1, 1), 'dy': random.uniform(-1, 1)}
    starlings.append(starling)

# Create predator
predator = {'x': width // 2, 'y': height // 2,
            'dx': random.uniform(-1, 1), 'dy': random.uniform(-1, 1)}


def move_starling(starling):
    # Separation
    min_distance = 5
    steer_x, steer_y, count = 0, 0, 0

    for other_starling in starlings:
        if starling != other_starling:
            distance_sq = (starling['x'] - other_starling['x'])**2 + (starling['y'] - other_starling['y'])**2
            if distance_sq < min_distance**2 and distance_sq > 0:  # Avoid division by zero
                diff_x = starling['x'] - other_starling['x']
                diff_y = starling['y'] - other_starling['y']
                steer_x += diff_x / distance_sq
                steer_y += diff_y / distance_sq
                count += 1

    if count > 0:
        steer_x /= count
        steer_y /= count
        magnitude = math.sqrt(steer_x**2 + steer_y**2)
        if magnitude > 0:  # Avoid division by zero
            steer_x /= magnitude
            steer_y /= magnitude

    # Alignment
    alignment_factor = 0.1
    avg_dx, avg_dy = 0, 0

    for other_starling in starlings:
        if starling != other_starling:
            avg_dx += other_starling['dx']
            avg_dy += other_starling['dy']

    avg_dx /= (num_starlings - 1)
    avg_dy /= (num_starlings - 1)

    steer_x += (avg_dx - starling['dx']) * alignment_factor
    steer_y += (avg_dy - starling['dy']) * alignment_factor

    # Cohesion
    cohesion_factor = 0.05
    avg_x, avg_y = 0, 0

    for other_starling in starlings:
        if starling != other_starling:
            avg_x += other_starling['x']
            avg_y += other_starling['y']

    avg_x /= (num_starlings - 1)
    avg_y /= (num_starlings - 1)

    steer_x += (avg_x - starling['x']) * cohesion_factor
    steer_y += (avg_y - starling['y']) * cohesion_factor

    # Predator Avoidance
    predator_distance_sq = (starling['x'] - predator['x'])**2 + (starling['y'] - predator['y'])**2
    if predator_distance_sq < 100:
        predator_avoidance_factor = 0.1
        steer_x += (starling['x'] - predator['x']) * predator_avoidance_factor
        steer_y += (starling['y'] - predator['y']) * predator_avoidance_factor

    # Randomness
    randomness_factor = 0.1
    steer_x += random.uniform(-randomness_factor, randomness_factor)
    steer_y += random.uniform(-randomness_factor, randomness_factor)

    starling['dx'] += steer_x
    starling['dy'] += steer_y

    # Limit the maximum speed
    max_speed = 2.0
    speed = math.sqrt(starling['dx']**2 + starling['dy']**2)
    if speed > max_speed:
        starling['dx'] *= max_speed / speed
        starling['dy'] *= max_speed / speed

    # Move the starling
    starling['x'] += starling['dx']
    starling['y'] += starling['dy']

    # Border checking
    if starling['x'] > width:
        starling['x'] = width
        starling['dx'] *= -1
    elif starling['x'] < 0:
        starling['x'] = 0
        starling['dx'] *= -1

    if starling['y'] > height:
        starling['y'] = height
        starling['dy'] *= -1
    elif starling['y'] < 0:
        starling['y'] = 0
        starling['dy'] *= -1


def move_predator():
    # Find the nearest starling
    min_distance_sq = float('inf')
    nearest_starling = None

    for starling in starlings:
        distance_sq = (predator['x'] - starling['x'])**2 + (predator['y'] - starling['y'])**2
        if distance_sq < min_distance_sq:
            min_distance_sq = distance_sq
            nearest_starling = starling

    # Steer towards the nearest starling
    if nearest_starling:
        steer_x = nearest_starling['x'] - predator['x']
        steer_y = nearest_starling['y'] - predator['y']
        magnitude = math.sqrt(steer_x**2 + steer_y**2)
        if magnitude > 0:
            steer_x /= magnitude
            steer_y /= magnitude

        # Adjust predator's direction and speed
        predator_speed = 1.5
        predator['dx'] = steer_x * predator_speed
        predator['dy'] = steer_y * predator_speed

    # Move the predator
    predator['x'] += predator['dx']
    predator['y'] += predator['dy']

    # Wrap around the screen
    if predator['x'] > width:
        predator['x'] = 0
    elif predator['x'] < 0:
        predator['x'] = width

    if predator['y'] > height:
        predator['y'] = 0
    elif predator['y'] < 0:
        predator['y'] = height


def distance(starling1, starling2):
    return math.sqrt((starling1['x'] - starling2['x'])**2 +
                     (starling1['y'] - starling2['y'])**2)


def update():
    for i in range(num_starlings):
        move_starling(starlings[i])

    move_predator()


def display_starlings(stdscr):
    stdscr.clear()
    for s in starlings:
        stdscr.addch(int(s['y']), int(s['x']), ord('.'))
    stdscr.addch(int(predator['y']), int(predator['x']), ord('P'))
    stdscr.refresh()


def main(stdscr):
    while True:
        display_starlings(stdscr)
        update()
        time.sleep(0.03)


# Start the simulation
if __name__ == "__main__":
    curses.wrapper(main)
