import random
import math
import curses
import time

# New screen dimensions (bigger size)
WIDTH, HEIGHT = 120, 40

# Starlings' properties
NUM_STARLINGS = 150
STARLING_SPEED = 2
STARLING_TURN_ANGLE = math.radians(45)

# Predator's properties
PREDATOR_SPEED = 2.5
PREDATOR_DAMAGE = 5
NUM_PREDATORS = 1

# Obstacles' properties
NUM_OBSTACLES = 30

# Attraction points' properties
NUM_ATTRACTION_POINTS = 5
ATTRACTION_STRENGTH = 0.001

# Starling health properties
STARLING_STARTING_HEALTH = 100
STARLING_HEALTH_DECAY_RATE = 0

# Function to calculate the angle between two points
def angle_between_points(p1, p2):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    return math.atan2(dy, dx)

# Function to calculate the distance between two points
def distance_between_points(p1, p2):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    return math.sqrt(dx**2 + dy**2)

# Starling class
class Starling:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = random.uniform(0, 2 * math.pi)
        self.health = STARLING_STARTING_HEALTH

    def move(self):
        # Move the starling in the current direction
        dx = STARLING_SPEED * math.cos(self.direction)
        dy = STARLING_SPEED * math.sin(self.direction)
        self.x += dx
        self.y += dy

        # Wrap around the screen edges
        if self.x < 0:
            self.x += WIDTH
        elif self.x >= WIDTH:
            self.x -= WIDTH
        if self.y < 0:
            self.y += HEIGHT
        elif self.y >= HEIGHT:
            self.y -= HEIGHT

        # Reduce health over time
        self.health -= STARLING_HEALTH_DECAY_RATE
        if self.health <= 0:
            self.health = 0

    def steer_towards(self, target_angle):
        # Calculate the angle difference between the current direction and target direction
        angle_diff = target_angle - self.direction

        # Ensure that the angle difference is between -pi and pi for smoother steering
        angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi

        # Steer towards the target angle
        if angle_diff > 0:
            self.direction += min(angle_diff, STARLING_TURN_ANGLE)
        else:
            self.direction -= min(-angle_diff, STARLING_TURN_ANGLE)

    def align(self, neighbors):
        if neighbors:
            average_direction = sum(s.direction for s in neighbors) / len(neighbors)
            self.steer_towards(average_direction)

# Predator class
class Predator:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = random.uniform(0, 2 * math.pi)
        self.health = 100

    def move(self):
        # Move the predator towards the closest starling
        closest_starling = min(starlings, key=lambda s: distance_between_points((self.x, self.y), (s.x, s.y)))
        target_angle = angle_between_points((self.x, self.y), (closest_starling.x, closest_starling.y))
        self.direction = target_angle

        dx = PREDATOR_SPEED * math.cos(self.direction)
        dy = PREDATOR_SPEED * math.sin(self.direction)
        self.x += dx
        self.y += dy

        # Wrap around the screen edges
        if self.x < 0:
            self.x += WIDTH
        elif self.x >= WIDTH:
            self.x -= WIDTH
        if self.y < 0:
            self.y += HEIGHT
        elif self.y >= HEIGHT:
            self.y -= HEIGHT

        # Reduce health over time
        self.health -= STARLING_HEALTH_DECAY_RATE
        if self.health <= 0:
            self.health = 0

# Obstacle class
class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# AttractionPoint class
class AttractionPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Function to display the predator
def display_predator(stdscr, x, y):
    try:
        stdscr.addstr(int(y), int(x), 'PP', curses.color_pair(3))
        stdscr.addstr(int(y) + 1, int(x), 'PP', curses.color_pair(3))
    except curses.error:
        pass

def main(stdscr):
    global starlings, predators, obstacles, attraction_points  # Declare all variables as global

    # Initialize curses
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(1)   # Non-blocking input
    stdscr.timeout(100) # Set a small timeout for getch()

    # Set up color pairs
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Starlings: Green on Black
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)   # Attraction points: Blue on Black
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)    # Predators: Red on Black

    # Create the initial objects (starlings, obstacles, etc.)
    starlings = [Starling(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)) for _ in range(NUM_STARLINGS)]
    obstacles = [Obstacle(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)) for _ in range(NUM_OBSTACLES)]
    attraction_points = [AttractionPoint(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)) for _ in range(NUM_ATTRACTION_POINTS)]
    predators = [Predator(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)) for _ in range(NUM_PREDATORS)]

    try:
        last_starling_spawn_time = time.time()
        last_predator_spawn_time = time.time()

        # Main loop
        while True:
            stdscr.clear()

            # Check if it's time to spawn new starlings
            current_time = time.time()
            if current_time - last_starling_spawn_time >= 5:
                for _ in range(int(NUM_STARLINGS * 0.7)):
                    starlings.append(Starling(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)))
                last_starling_spawn_time = current_time

            # Check if it's time to spawn a new predator
            if current_time - last_predator_spawn_time >= 10:
                predators.append(Predator(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)))
                last_predator_spawn_time = current_time

            # Move and display the predators
            for predator in predators:
                predator.move()
                display_predator(stdscr, predator.x, predator.y)

            # Get the average direction of nearby starlings for alignment behavior
            for starling in starlings:
                neighbors = [s for s in starlings if s != starling and distance_between_points((starling.x, starling.y), (s.x, s.y)) < 15]
                starling.align(neighbors)

                # Avoid obstacles and predator
                for obstacle in obstacles:
                    if distance_between_points((starling.x, starling.y), (obstacle.x, obstacle.y)) < 6:
                        target_angle = angle_between_points((starling.x, starling.y), (obstacle.x, obstacle.y))
                        starling.steer_towards(target_angle + math.pi)

                        # Reduce health when colliding with an obstacle
                        starling.health -= 5

                for predator in predators:
                    if distance_between_points((starling.x, starling.y), (predator.x, predator.y)) < 4:
                        target_angle = angle_between_points((starling.x, starling.y), (predator.x, predator.y))
                        starling.steer_towards(target_angle + math.pi)

                        # Reduce health when caught by the predator
                        starling.health -= PREDATOR_DAMAGE

                # Attraction to points
                for attraction_point in attraction_points:
                    target_angle = angle_between_points((starling.x, starling.y), (attraction_point.x, attraction_point.y))
                    starling.steer_towards(target_angle)

            # Move the starlings
            for starling in starlings:
                starling.move()

            # Remove dead starlings
            starlings = [starling for starling in starlings if starling.health > 0]

            # Display the obstacles
            for obstacle in obstacles:
                if 0 <= int(obstacle.y) < HEIGHT and 0 <= int(obstacle.x) < WIDTH:
                    try:
                        stdscr.addch(int(obstacle.y), int(obstacle.x), 'X')
                    except curses.error:
                        pass  # Ignore error when adding a character outside the screen

            # Display the attraction points
            for attraction_point in attraction_points:
                if 0 <= int(attraction_point.y) < HEIGHT and 0 <= int(attraction_point.x) < WIDTH:
                    try:
                        stdscr.addch(int(attraction_point.y), int(attraction_point.x), '+', curses.color_pair(2))
                    except curses.error:
                        pass

            # Display the current positions of starlings
            for starling in starlings:
                try:
                    stdscr.addch(int(starling.y), int(starling.x), '*', curses.color_pair(1))
                except curses.error:
                    pass

            stdscr.refresh()
            time.sleep(0.05)  # Adjust the sleep duration for animation speed

            # Check for user input (quit the animation with 'q')
            ch = stdscr.getch()
            if ch == ord('q'):
                break

    finally:
        # Clean up curses
        curses.endwin()

curses.wrapper(main)
