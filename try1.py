import pygame
import sys
import time
from pygame.locals import QUIT, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT

from point import Point

# Initialize Pygame
pygame.init()

# Constants
PIXELS_PER_CM = 2.5
DETECTION_RANGE_CM = 300 # 300
DETECTION_RANGE_PX = int(DETECTION_RANGE_CM / PIXELS_PER_CM)
DRONE_RADIUS_CM = 10
DRONE_RADIUS_PX = int(DRONE_RADIUS_CM / PIXELS_PER_CM)
SENSOR_RATE = 10  # 10 times per second
BATTERY_LIFE_MINUTES = 8
BATTERY_LIFE_SECONDS = BATTERY_LIFE_MINUTES * 60
DRONE_SPEED_CM_PER_SEC = 400  # 100 # 1 meter per second
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



"""
Function to load and display the map
this is the main loop that displays the map 
call functions 
and waits fro movement directions 
"""
def display_map(image_path, drone_pos_cm):

    map_image = pygame.image.load(image_path) # Load the image
    map_width, map_height = map_image.get_size() # Get the size of the image in pixels
    screen = pygame.display.set_mode((map_width, map_height)) # Create a window with the size of the image
    pygame.display.set_caption('Map Viewer')

    # drone_pos_px = [drone_pos_cm[0] / PIXELS_PER_CM, drone_pos_cm[1] / PIXELS_PER_CM] # Convert initial drone position from cm to pixels
    drone_pos_px = [drone_pos_cm[0], drone_pos_cm[1]]

    start_time = time.time() # Start time
    font = pygame.font.Font(None, 24) # Font for displaying text

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
            elif event.type == KEYDOWN:
                new_pos_px = drone_pos_px.copy()  # Added line
                if event.key == K_UP:
                    new_pos_px[1] -= DRONE_SPEED_PX_PER_SEC / SENSOR_RATE
                elif event.key == K_DOWN:
                    new_pos_px[1] += DRONE_SPEED_PX_PER_SEC / SENSOR_RATE
                elif event.key == K_LEFT:
                    new_pos_px[0] -= DRONE_SPEED_PX_PER_SEC / SENSOR_RATE
                elif event.key == K_RIGHT:
                    new_pos_px[0] += DRONE_SPEED_PX_PER_SEC / SENSOR_RATE

                print("pos x: " + str(new_pos_px[0]) + "  pos y: " + str(new_pos_px[1]))

                # # Check if the new position is within the white area
                # new_x, new_y = int(new_pos_px[0]), int(new_pos_px[1])
                # if 0 <= new_x < map_width and 0 <= new_y < map_height:
                #     color = map_image.get_at((new_x, new_y))
                #     if color == WHITE or color == YELLOW:
                #         drone_pos_px = new_pos_px  # Update only if the new position is valid

                # Check if the new position is within the white area and adjust if too close to walls
                if validate_and_adjust_position(new_pos_px, map_image, map_width, map_height):
                    drone_pos_px = new_pos_px  # Update only if the new position is valid


        screen.blit(map_image, (0, 0)) # Draw the image onto the screen
        draw_drone_and_detect(screen, drone_pos_px, map_image) # Draw the drone and its detection range on the map
        draw_text(screen, f"Time Remaining: {minutes_remaining:02d}:{seconds_remaining:02d}", font, TEXT_COLOR,(10, 10)) # Draw the time remaining
        pygame.display.update() # Update the display

        """
        this may need updating or deleting
        """
        time.sleep(1 / SENSOR_RATE) # Sleep to simulate the sensor update rate


def validate_and_adjust_position(drone_pos_px, map_image, map_width, map_height):
    safe_distance_px = int(25 / PIXELS_PER_CM)

    new_x, new_y = int(drone_pos_px[0]), int(drone_pos_px[1])

    # Ensure the new position is within map boundaries
    if not (0 <= new_x < map_width and 0 <= new_y < map_height):
        return False

    # Get the surrounding area within the safe distance
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

# Function to draw the drone and its detection range on the map
def draw_drone_and_detect(screen, drone_pos_px, map_image):
    center_x, center_y = int(drone_pos_px[0]), int(drone_pos_px[1])

    # Detect and color the area
    detect_and_color(screen, center_x, center_y, map_image)

    # Draw the drone as a circle
    pygame.draw.circle(screen, RED, (center_x, center_y), DRONE_RADIUS_PX)
"""
Function to detect the map area and color it yellow
this needs to happen 10 times per second !!
"""
def detect_and_color(screen, center_x, center_y, map_image):
    # Draw the points from POINT_HISTORY
    for point in POINT_HISTORY:
        pygame.draw.circle(screen, GREEN, (point.x, point.y), DRONE_RADIUS_PX)

    directions = [
        (0, -DETECTION_RANGE_PX),  # Forward (up)
        (0, DETECTION_RANGE_PX),  # Backward (down)
        (DETECTION_RANGE_PX, 0),  # Right
        (-DETECTION_RANGE_PX, 0)  # Left
    ]

    # Count the number of infinite directions
    inf_count = 0
    inf_directions = []

    for dx, dy in directions:
        for i in range(1, DETECTION_RANGE_PX + 1):
            x = center_x + dx * i // DETECTION_RANGE_PX
            y = center_y + dy * i // DETECTION_RANGE_PX
            if 0 <= x < screen.get_width() and 0 <= y < screen.get_height():
                color = screen.get_at((x, y))
                if i == DETECTION_RANGE_PX  and color == WHITE:
                    inf_count += 1
                    inf_directions.append((dx, dy))
                if color == WHITE:
                    screen.set_at((x, y), YELLOW)
                    map_image.set_at((x, y), YELLOW)
                elif color == BLACK:
                    break

    if inf_count >= 2:
        Point_displacement(screen,center_x, center_y,inf_directions)
def Point_displacement(screen,center_x, center_y, inf_directions): # fix do calculations in detect and color !!!!!
    # Assuming the drone's current position is the center of the point
    new_point = Point(center_x, center_y)

    # Update the infinite directions in the Point object
    for dx, dy in inf_directions:
        if dx == 0 and dy < 0:
            new_point.inf_front = True
        elif dx == 0 and dy > 0:
            new_point.inf_back = True
        elif dx > 0 and dy == 0:
            new_point.inf_right = True
        elif dx < 0 and dy == 0:
            new_point.inf_left = True

    # Add the Point object to POINT_HISTORY
    POINT_HISTORY.append(new_point)
    # pygame.draw.circle(screen, GREEN, (center_x, center_y), DRONE_RADIUS_PX)

    # Print the point for testing purposes
    print("New Point:", new_point)


"""
Function to draw text on the screen
and may be deleted and simply moved to the main loop in display_map 
"""
def draw_text(screen, text, font, color, position):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

# Main function
if __name__ == "__main__":
    # Path to the image file
    image_path = "C:\\Users\\dovy4\\Desktop\\אוניברסיטה גיבוי 3.3.2022\\שנה ד סמסטר ב\\רובוטים אוטונומיים\\מטלה 1\\EX1\\Maps\\p11.png"

    # Drone position in cm (x, y)
    drone_position_cm = (110, 70)  # Example position

    display_map(image_path, drone_position_cm)
