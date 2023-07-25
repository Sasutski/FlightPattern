import random
import math
import curses
import time

# New screen dimensions (bigger size)
WIDTH, HEIGHT = 150, 50

# Starlings' properties
NUM_STARLINGS = 150
STARLING_SPEED = 1
STARLING_TURN_ANGLE = math.radians(30)

# Predator's properties
PREDATOR_SPEED = 2.0
PREDATOR_DAMAGE = 5
NUM_PREDATORS = 1

# Obstacles' properties
NUM_OBSTACLES = 30

# Attraction points' properties
NUM_ATTRACTION_POINTS = 5
ATTRACTION_STRENGTH = 0.01

# Starling health properties
STARLING_STARTING_HEALTH = 100
STARLING_HEALTH_DECAY_RATE = 0.2

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

# Attraction point class
class AttractionPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Function to spawn new starlings
def spawn_starlings():
    num_to_spawn = int(NUM_STARLINGS * 0.7)
    for _ in range(num_to_spawn):
        new_starling = Starling(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
        starlings.append(new_starling)

# Function to spawn new predators
def spawn_predators():
    new_predator = Predator(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
    predators.append(new_predator)

# Create starlings with updated initial positions
starlings = [Starling(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)) for _ in range(NUM_STARLINGS)]

# Create obstacles with updated initial positions
obstacles = [Obstacle(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)) for _ in range(NUM_OBSTACLES)]

# Create attraction points with updated initial positions
attraction_points = [AttractionPoint(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)) for _ in range(NUM_ATTRACTION_POINTS)]

# Create predator list with updated initial positions
predators = [Predator(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)) for _ in range(NUM_PREDATORS)]

# Initialize curses
stdscr = curses.initscr()
curses.curs_set(0)  # Hide the cursor
stdscr.nodelay(1)   # Non-blocking input
stdscr.timeout(100) # Set a small timeout for getch()
curses.start_color()
curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)    # Define color pair for starlings
curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Define color pair for predator

try:
    last_starling_spawn_time = time.time()
    last_predator_spawn_time = time.time()

    # Main loop
    while True:
        stdscr.clear()

        # Check if it's time to spawn new starlings
        current_time = time.time()
        if current_time - last_starling_spawn_time >= 5:
            spawn_starlings()
            last_starling_spawn_time = current_time

        # Check if it's time to spawn a new predator
        if current_time - last_predator_spawn_time >= 10:
            spawn_predators()
            last_predator_spawn_time = current_time

        # Move and display the predators
        for predator in predators:
            predator.move()
            try:
                stdscr.addch(int(predator.y), int(predator.x), 'P', curses.color_pair(2))
            except curses.error:
                pass  # Ignore error when adding a character outside the screen

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
                    stdscr.addch(int(attraction_point.y), int(attraction_point.x), '+')
                except curses.error:
                    pass  # Ignore error when adding a character outside the screen

        # Display the current positions of starlings
        for starling in starlings:
            try:
                stdscr.addch(int(starling.y), int(starling.x), '*', curses.color_pair(1))
            except curses.error:
                pass  # Ignore error when adding a character outside the screen

        stdscr.refresh()
        time.sleep(0.05)  # Adjust the sleep duration for animation speed

        # Check for user input (quit the animation with 'q')
        ch = stdscr.getch()
        if ch == ord('q'):
            break

finally:
    # Clean up curses
    curses.endwin()
