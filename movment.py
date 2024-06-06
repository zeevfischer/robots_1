import pygame
import sys
import time
from pygame.locals import QUIT, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT

from point import Point

# Initialize Pygame
pygame.init()

# Constants
PIXELS_PER_CM = 2.5
DETECTION_RANGE_CM = 300  # 300
DETECTION_RANGE_PX = int(DETECTION_RANGE_CM / PIXELS_PER_CM)
DRONE_RADIUS_CM = 10
DRONE_RADIUS_PX = int(DRONE_RADIUS_CM / PIXELS_PER_CM)
SENSOR_RATE = 10  # 10 times per second
BATTERY_LIFE_MINUTES = 8
BATTERY_LIFE_SECONDS = BATTERY_LIFE_MINUTES * 60
DRONE_SPEED_CM_PER_SEC = 100  # 100 # 1 meter per second
DRONE_SPEED_PX_PER_SEC = int(DRONE_SPEED_CM_PER_SEC / PIXELS_PER_CM)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
TEXT_COLOR = (255, 255, 255)
POINT_HISTORY = []

# Global variables for detection distances
detect_distance_up = float('inf')
detect_distance_down = float('inf')
detect_distance_right = float('inf')
detect_distance_left = float('inf')


def display_map(image_path, drone_pos_cm):
    map_image = pygame.image.load(image_path)  # Load the image
    map_width, map_height = map_image.get_size()  # Get the size of the image in pixels
    screen = pygame.display.set_mode((map_width, map_height))  # Create a window with the size of the image
    pygame.display.set_caption('Map Viewer')

    drone_pos_px = [drone_pos_cm[0], drone_pos_cm[1]]

    start_time = time.time()  # Start time
    font = pygame.font.Font(None, 24)  # Font for displaying text

    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        time_remaining = max(0, BATTERY_LIFE_SECONDS - elapsed_time)
        minutes_remaining = int(time_remaining // 60)
        seconds_remaining = int(time_remaining % 60)

        # Detect and color the map
        detect_and_color_map(screen, drone_pos_px, map_image)

        # Move to the farthest detected point
        move_to_farthest_point(drone_pos_px, map_image)

        screen.blit(map_image, (0, 0))  # Draw the image onto the screen
        draw_drone(screen, drone_pos_px)  # Draw the drone on the map
        draw_text(screen, f"Time Remaining: {minutes_remaining:02d}:{seconds_remaining:02d}", font, TEXT_COLOR,
                  (10, 10))  # Draw the time remaining
        pygame.display.update()  # Update the display

        time.sleep(1 / SENSOR_RATE)  # Sleep to simulate the sensor update rate


def detect_and_color_map(screen, drone_pos_px, map_image):
    global detect_distance_up, detect_distance_down, detect_distance_left, detect_distance_right

    center_x, center_y = int(drone_pos_px[0]), int(drone_pos_px[1])
    pygame.draw.circle(screen, RED, (center_x, center_y), DRONE_RADIUS_PX)

    directions = [(x, y) for x in range(-1, 2) for y in range(-1, 2) if not (x == 0 and y == 0)]
    max_distance = 0
    farthest_point = None

    for dx, dy in directions:
        detected_distance = float('inf')
        for i in range(1, DETECTION_RANGE_PX + 1):
            x = center_x + dx * i
            y = center_y + dy * i
            if 0 <= x < screen.get_width() and 0 <= y < screen.get_height():
                color = screen.get_at((x, y))
                if color == WHITE:
                    screen.set_at((x, y), YELLOW)
                    map_image.set_at((x, y), YELLOW)
                    detected_distance = i
                    if detected_distance > max_distance:
                        max_distance = detected_distance
                        farthest_point = (x, y)
                elif color == BLACK:
                    break

    if farthest_point:
        POINT_HISTORY.append(Point(farthest_point[0], farthest_point[1]))


def move_to_farthest_point(drone_pos_px, map_image):
    if not POINT_HISTORY:
        return

    farthest_point = POINT_HISTORY[-1]
    new_pos_px = move_drone(drone_pos_px, (farthest_point.x, farthest_point.y))
    if new_pos_px:
        drone_pos_px[0] = new_pos_px[0]
        drone_pos_px[1] = new_pos_px[1]


def move_drone(current_pos_px, target_pos_px):
    dx = target_pos_px[0] - current_pos_px[0]
    dy = target_pos_px[1] - current_pos_px[1]
    distance = (dx ** 2 + dy ** 2) ** 0.5

    if distance == 0:
        return None

    move_distance = min(DRONE_SPEED_PX_PER_SEC / SENSOR_RATE, distance)
    ratio = move_distance / distance

    new_x = current_pos_px[0] + dx * ratio
    new_y = current_pos_px[1] + dy * ratio

    return [new_x, new_y]


def draw_drone(screen, drone_pos_px):
    center_x, center_y = int(drone_pos_px[0]), int(drone_pos_px[1])
    pygame.draw.circle(screen, RED, (center_x, center_y), DRONE_RADIUS_PX)
    for point in POINT_HISTORY:
        pygame.draw.circle(screen, GREEN, (point.x, point.y), DRONE_RADIUS_PX)


def draw_text(screen, text, font, color, position):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)


if __name__ == "__main__":
    image_path = "C:\\Users\\dovy4\\Desktop\\אוניברסיטה גיבוי 3.3.2022\\שנה ד סמסטר ב\\רובוטים אוטונומיים\\מטלה 1\\EX1\\Maps\\p11.png"
    drone_position_cm = (110, 70)  # Example position
    display_map(image_path, drone_position_cm)
