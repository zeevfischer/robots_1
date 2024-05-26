import pygame
import sys
import time
from pygame.locals import QUIT

from point import Point

# Initialize Pygame
pygame.init()

# Constants
PIXELS_PER_CM = 2.5
DETECTION_RANGE_CM = 300
DETECTION_RANGE_PX = int(DETECTION_RANGE_CM / PIXELS_PER_CM)
DRONE_RADIUS_CM = 10
DRONE_RADIUS_PX = int(DRONE_RADIUS_CM / PIXELS_PER_CM)
SENSOR_RATE = 10  # 10 times per second
BATTERY_LIFE_MINUTES = 8
BATTERY_LIFE_SECONDS = BATTERY_LIFE_MINUTES * 60
DRONE_SPEED_CM_PER_SEC = 100  # 1 meter per second
DRONE_SPEED_PX_PER_SEC = int(DRONE_SPEED_CM_PER_SEC / PIXELS_PER_CM)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
TEXT_COLOR = (255, 255, 255)
POINT_HISTORY = []

"""
TO DO
1 adjust the distance the drone can be from the wall !! now it can reach to close 
2 movement algo 
3 GREEN point position
4 percentage of map that has been seen   
5 make sure that all the numbers are correct 10 times per second and all of that !
6 see the assignment directions if more things are needed to be done !
7 change names to match assignment
8 add pitch and roll
"""

# Load the map image
image_path = "C:\\Users\\dovy4\\Desktop\\אוניברסיטה גיבוי 3.3.2022\\שנה ד סמסטר ב\\רובוטים אוטונומיים\\מטלה 1\\EX1\\Maps\\p12.png"
map_image = pygame.image.load(image_path)
map_width, map_height = map_image.get_size()


def display_map(image_path, drone_pos_cm):
    screen = pygame.display.set_mode((map_width, map_height))
    pygame.display.set_caption('Map Viewer')

    drone_pos_px = [drone_pos_cm[0], drone_pos_cm[1]]
    start_time = time.time()
    font = pygame.font.Font(None, 24)

    movement_direction = (0, -1)

    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        time_remaining = max(0, BATTERY_LIFE_SECONDS - elapsed_time)
        minutes_remaining = int(time_remaining // 60)
        seconds_remaining = int(time_remaining % 60)

        for event in pygame.event.get():
            if event.type == QUIT or elapsed_time >= BATTERY_LIFE_SECONDS:
                pygame.quit()
                sys.exit()

        # Move the drone according to the movement algorithm
        new_pos_px, movement_direction = move_drone(drone_pos_px, map_image, movement_direction)
        if new_pos_px is not None:
            drone_pos_px = new_pos_px

        screen.blit(map_image, (0, 0))
        draw_drone_and_detect(screen, drone_pos_px, map_image)
        draw_text(screen, f"Time Remaining: {minutes_remaining:02d}:{seconds_remaining:02d}", font, TEXT_COLOR, (10, 10))
        pygame.display.update()
        time.sleep(1 / SENSOR_RATE)


def move_drone(current_pos_px, map_image, movement_direction):
    dx, dy = movement_direction
    new_x = current_pos_px[0] + dx
    new_y = current_pos_px[1] + dy

    if 0 <= new_x < map_width and 0 <= new_y < map_height:
        if validate_and_adjust_position([new_x, new_y], map_image):
            return [new_x, new_y], movement_direction

    movement_direction = (movement_direction[1], -movement_direction[0])
    new_x = current_pos_px[0] + movement_direction[0]
    new_y = current_pos_px[1] + movement_direction[1]

    if 0 <= new_x < map_width and 0 <= new_y < map_height:
        if validate_and_adjust_position([new_x, new_y], map_image):
            return [new_x, new_y], movement_direction

    return None, movement_direction


def validate_and_adjust_position(drone_pos_px, map_image):
    safe_distance_px = int(25 / PIXELS_PER_CM)

    new_x, new_y = int(drone_pos_px[0]), int(drone_pos_px[1])

    if not (0 <= new_x < map_width and 0 <= new_y < map_height):
        return False

    for dx in range(-safe_distance_px, safe_distance_px + 1):
        for dy in range(-safe_distance_px, safe_distance_px + 1):
            check_x = new_x + dx
            check_y = new_y + dy
            if 0 <= check_x < map_width and 0 <= check_y < map_height:
                color = map_image.get_at((check_x, check_y))
                if color == BLACK:
                    return False

    color = map_image.get_at((new_x, new_y))
    return color == WHITE or color == YELLOW


def draw_drone_and_detect(screen, drone_pos_px, map_image):
    center_x, center_y = int(drone_pos_px[0]), int(drone_pos_px[1])

    detect_and_color(screen, center_x, center_y, map_image)

    pygame.draw.circle(screen, RED, (center_x, center_y), DRONE_RADIUS_PX)


def detect_and_color(screen, center_x, center_y, map_image):
    for point in POINT_HISTORY:
        pygame.draw.circle(screen, GREEN, (point.x, point.y), DRONE_RADIUS_PX)

    directions = [
        (0, -1),  # Up
        (0, 1),   # Down
        (1, 0),   # Right
        (-1, 0)   # Left
    ]

    inf_count = 0
    inf_directions = []

    for dx, dy in directions:
        for i in range(1, DETECTION_RANGE_PX + 1):
            x = center_x + dx * i
            y = center_y + dy * i
            if 0 <= x < screen.get_width() and 0 <= y < screen.get_height():
                color = screen.get_at((x, y))
                if i == DETECTION_RANGE_PX and color == WHITE:
                    inf_count += 1
                    inf_directions.append((dx, dy))
                if color == WHITE:
                    screen.set_at((x, y), YELLOW)
                    map_image.set_at((x, y), YELLOW)
                elif color == BLACK:
                    break

    if inf_count >= 2:
        point_displacement(screen, center_x, center_y, inf_directions)


def point_displacement(screen, center_x, center_y, inf_directions):
    new_point = Point(center_x, center_y)

    for dx, dy in inf_directions:
        if dx == 0 and dy < 0:
            new_point.inf_front = True
        elif dx == 0 and dy > 0:
            new_point.inf_back = True
        elif dx > 0 and dy == 0:
            new_point.inf_right = True
        elif dx < 0 and dy == 0:
            new_point.inf_left = True

    POINT_HISTORY.append(new_point)
    print("New Point:", new_point)


def draw_text(screen, text, font, color, position):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)


if __name__ == "__main__":
    drone_position_cm = (110, 70)
    display_map(image_path, drone_position_cm)
