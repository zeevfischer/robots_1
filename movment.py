import pygame
import sys
import time
import random
from pygame.locals import QUIT, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT

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
DRONE_SPEED_CM_PER_SEC = 1000  # 1 meter per second
DRONE_SPEED_PX_PER_SEC = int(DRONE_SPEED_CM_PER_SEC / PIXELS_PER_CM)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
TEXT_COLOR = (255, 255, 255)


# Function to load and display the map
def display_map(image_path, drone_pos_cm):
    # Load the image
    map_image = pygame.image.load(image_path)

    # Get the size of the image in pixels
    map_width, map_height = map_image.get_size()

    # Create a window with the size of the image
    screen = pygame.display.set_mode((map_width, map_height))
    pygame.display.set_caption('Map Viewer')

    # Convert initial drone position from cm to pixels
    drone_pos_px = [drone_pos_cm[0] / PIXELS_PER_CM, drone_pos_cm[1] / PIXELS_PER_CM]

    # Start time
    start_time = time.time()

    # Font for displaying text
    font = pygame.font.Font(None, 24)

    # Main loop to keep the window open
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

        # Move the drone
        move_drone(map_image, drone_pos_px)

        # Draw the image onto the screen
        screen.blit(map_image, (0, 0))

        # Draw the drone and its detection range on the map
        draw_drone_and_detect(screen, drone_pos_px, map_image)

        # Draw the time remaining
        draw_text(screen, f"Time Remaining: {minutes_remaining:02d}:{seconds_remaining:02d}", font, TEXT_COLOR,
                  (10, 10))

        # Update the display
        pygame.display.update()

        # Sleep to simulate the sensor update rate
        time.sleep(1 / SENSOR_RATE)


# Function to move the drone
def move_drone(map_image, drone_pos_px):
    # Calculate the next position
    next_pos_px = list(drone_pos_px)

    # Determine the direction of movement based on the current position and the direction with the most white pixels
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Right, Left, Down, Up
    max_white_pixels = -1
    best_direction = (0, 0)

    for dx, dy in directions:
        x = int(drone_pos_px[0] + dx * DETECTION_RANGE_PX)
        y = int(drone_pos_px[1] + dy * DETECTION_RANGE_PX)
        if 0 <= x < map_image.get_width() and 0 <= y < map_image.get_height():
            white_pixels = 0
            for i in range(DETECTION_RANGE_PX):
                x_pos = int(drone_pos_px[0] + dx * i)
                y_pos = int(drone_pos_px[1] + dy * i)
                if map_image.get_at((x_pos, y_pos)) == WHITE:
                    white_pixels += 1
            if white_pixels > max_white_pixels:
                max_white_pixels = white_pixels
                best_direction = (dx, dy)

    next_pos_px[0] += best_direction[0] * DRONE_SPEED_PX_PER_SEC / SENSOR_RATE
    next_pos_px[1] += best_direction[1] * DRONE_SPEED_PX_PER_SEC / SENSOR_RATE

    # Update the drone position
    drone_pos_px[:] = next_pos_px


# Function to draw the drone and its detection range on the map
def draw_drone_and_detect(screen, drone_pos_px, map_image):
    center_x, center_y = int(drone_pos_px[0]), int(drone_pos_px[1])

    # Detect and color the area
    detect_and_color(screen, center_x, center_y, map_image)

    # Draw the drone as a circle
    pygame.draw.circle(screen, RED, (center_x, center_y), DRONE_RADIUS_PX)


# Function to detect the map area and color it yellow using flood fill algorithm
# Function to detect the map area and color it yellow
def detect_and_color(screen, center_x, center_y, map_image):
    directions = [
        (0, -DETECTION_RANGE_PX),  # Forward (up)
        (0, DETECTION_RANGE_PX),  # Backward (down)
        (DETECTION_RANGE_PX, 0),  # Right
        (-DETECTION_RANGE_PX, 0)  # Left
    ]

    for dx, dy in directions:
        for i in range(1, DETECTION_RANGE_PX + 1):
            x = center_x + dx * i // DETECTION_RANGE_PX
            y = center_y + dy * i // DETECTION_RANGE_PX
            if 0 <= x < screen.get_width() and 0 <= y < screen.get_height():
                color = map_image.get_at((x, y))
                if color == WHITE:
                    screen.set_at((x, y), YELLOW)


# Function to draw text on the screen
def draw_text(screen, text, font, color, position):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)


# Main function
if __name__ == "__main__":
    # Path to the image file
    image_path = "C:\\Users\\dovy4\\Desktop\\אוניברסיטה גיבוי 3.3.2022\\שנה ד סמסטר ב\\רובוטים אוטונומיים\\מטלה 1\\EX1\\Maps\\p11.png"

    # Drone position in cm (x, y)
    drone_position_cm = (300, 150)  # Example position

    display_map(image_path, drone_position_cm)