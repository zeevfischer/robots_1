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

    drone_pos_px = [drone_pos_cm[0], drone_pos_cm[1]]

    start_time = time.time() # Start time
    font = pygame.font.Font(None, 24) # Font for displaying text

    # Main loop to keep the window open
    # old_direction = []
    # calculate the closest wall for start
    direction = closest_wall_direction(screen, drone_pos_px)
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        time_remaining = max(0, BATTERY_LIFE_SECONDS - elapsed_time)
        minutes_remaining = int(time_remaining // 60)
        seconds_remaining = int(time_remaining % 60)

        # movement
        potential_position = move_drone(drone_pos_px,map_image,direction)

        # validate position !!!
        if 0 <= potential_position[0] < map_width and 0 <= potential_position[1] < map_height:

            # if (direction == [0,-1] and detect_distance_up <= 25) or (direction == [0,1] and detect_distance_down <= 25) or (direction == [1,0] and detect_distance_right <= 25) or (direction == [-1,0] and detect_distance_left <= 25): # direction will only change if i cant move in my current direction
            #     # go to farthest inf detected
            #     direction = direction_change(old_direction)
            #     potential_position = move_drone(drone_pos_px, map_image, direction)

            if validate_and_adjust_position(potential_position, map_image, map_width, map_height):
                drone_pos_px = potential_position
            else:
                # old_direction = direction
                direction = direction_change(direction)




        # # if we got there and cant move !
        # if drone_pos_px[0] == old_drone_pos_px[0] and drone_pos_px[1] == old_drone_pos_px[1]:
        #     # go to farthest inf detected
        #     empty_space_direction(direction)










        # for event in pygame.event.get():
        #     if event.type == QUIT or elapsed_time >= BATTERY_LIFE_SECONDS:
        #         pygame.quit()
        #         sys.exit()
        #     elif event.type == KEYDOWN:
        #         new_pos_px = drone_pos_px.copy()  # Added line
        #         if event.key == K_UP:
        #             new_pos_px[1] -= DRONE_SPEED_PX_PER_SEC / SENSOR_RATE
        #         elif event.key == K_DOWN:
        #             new_pos_px[1] += DRONE_SPEED_PX_PER_SEC / SENSOR_RATE
        #         elif event.key == K_LEFT:
        #             new_pos_px[0] -= DRONE_SPEED_PX_PER_SEC / SENSOR_RATE
        #         elif event.key == K_RIGHT:
        #             new_pos_px[0] += DRONE_SPEED_PX_PER_SEC / SENSOR_RATE
        #
        #         print("pos x: " + str(new_pos_px[0]) + "  pos y: " + str(new_pos_px[1]))
        #
        #         # # Check if the new position is within the white area
        #         # new_x, new_y = int(new_pos_px[0]), int(new_pos_px[1])
        #         # if 0 <= new_x < map_width and 0 <= new_y < map_height:
        #         #     color = map_image.get_at((new_x, new_y))
        #         #     if color == WHITE or color == YELLOW:
        #         #         drone_pos_px = new_pos_px  # Update only if the new position is valid
        #
        #         # Check if the new position is within the white area and adjust if too close to walls
        #         if validate_and_adjust_position(new_pos_px, map_image, map_width, map_height):
        #             drone_pos_px = new_pos_px  # Update only if the new position is valid
        #
        #
        screen.blit(map_image, (0, 0)) # Draw the image onto the screen
        draw_drone_detect_and_color(screen, drone_pos_px, map_image) # Draw the drone and its detection range on the map
        draw_text(screen, f"Time Remaining: {minutes_remaining:02d}:{seconds_remaining:02d}", font, TEXT_COLOR,(10, 10)) # Draw the time remaining
        pygame.display.update() # Update the display

        """
        this may need updating or deleting
        """
        time.sleep(1 / SENSOR_RATE) # Sleep to simulate the sensor update rate

'''
now we need a function that will take us in a different direction after reaching the nearest wall 
ideally to the place where we detect more space not less !
'''
def direction_change(old_direction):
    directions = [
        (0, -1),  # Up
        (0, 1),  # Down
        (1, 0),  # Right
        (-1, 0)  # Left
    ]
    direction = []
    # we went up down
    if old_direction[0] == 0:
        if detect_distance_left > detect_distance_right:
            # we go left
            direction = [-1,0]
        else:
            # we go right
            direction = [1,0]
    # we went left right
    if old_direction[1] == 0:
        if detect_distance_up > detect_distance_down:
            # we go up
            direction = [0,-1]
        else:
            # we go down
            direction = [0,1]
    return direction

'''
the drone needs to move 100m per second
the calculation may not be in this function ass it also needs to draw and detect 10 times in this movement  
so here we will move it DRONE_SPEED_CM_PER_SEC/SENSOR_RATE 
'''
def closest_wall_direction(screen, drone_pos_px):
    directions = [
        (0, -1),  # Up
        (0, 1),  # Down
        (1, 0),  # Right
        (-1, 0)  # Left
    ]

    min_dist = float('inf')
    direction = (0, 0)

    for dx, dy in directions:
        for i in range(1, DETECTION_RANGE_PX + 1):
            x = drone_pos_px[0] + dx * i
            y = drone_pos_px[1] + dy * i
            if 0 <= x < screen.get_width() and 0 <= y < screen.get_height():
                color = screen.get_at((int(x), int(y)))
                if color == BLACK:
                    dist = i
                    if dist < min_dist:
                        min_dist = dist
                        direction = [dx, dy]
                    break

    return direction
'''
this code needs to be adjusted to only move the drone and not validate the position 
'''
def move_drone(current_pos_px, map_image, movement_direction):
    map_width, map_height = map_image.get_size()
    dx = movement_direction[0]
    dy = movement_direction[1]
    if(dx == 0):
        new_x = current_pos_px[0]
    else:
        new_x = current_pos_px[0] + ((DRONE_SPEED_PX_PER_SEC/SENSOR_RATE) * dx)
    if(dy == 0):
        new_y = current_pos_px[1]
    else:
        new_y = current_pos_px[1] + ((DRONE_SPEED_PX_PER_SEC / SENSOR_RATE) * dy)

    new_pos_px =[new_x,new_y]
    return new_pos_px
'''
this returns true or false if the new position is good 
'''
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
    # this already returns true or false
    return color == WHITE or color == YELLOW
# Function to draw the drone and its detection range on the map
"""
Function to detect the map area and color it yellow
this needs to happen 10 times per second !!
"""
def draw_drone_detect_and_color(screen, drone_pos_px, map_image):
    global detect_distance_up,detect_distance_down,detect_distance_left,detect_distance_right
    center_x, center_y = int(drone_pos_px[0]), int(drone_pos_px[1])
    pygame.draw.circle(screen, RED, (center_x, center_y), DRONE_RADIUS_PX)
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
        detected_distance = float('inf')
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
                    detected_distance = i
                    break
        if dx == 0 and dy < 0:
            detect_distance_up = detected_distance
        elif dx == 0 and dy > 0:
            detect_distance_down = detected_distance
        elif dx > 0 and dy == 0:
            detect_distance_right = detected_distance
        elif dx < 0 and dy == 0:
            detect_distance_left = detected_distance

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
