import pygame
import sys
from pygame.locals import QUIT

# Initialize Pygame
pygame.init()

# Function to load and display the map
def display_map(image_path ,drone_position_cm):
    # Load the image
    map_image = pygame.image.load(image_path)

    # Get the size of the image
    map_width, map_height = map_image.get_size()
    print("map_width: = " + str(map_width))
    print("map_height: = " + str(map_height))

    # Create a window with the size of the image
    screen = pygame.display.set_mode((map_width, map_height))
    pygame.display.set_caption('Map Viewer')

    # Main loop to keep the window open
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # Draw the image onto the screen
        screen.blit(map_image, (0, 0))

        # Draw the drone on the map
        draw_drone(screen, drone_position_cm)

        # Update the display
        pygame.display.update()


# Function to draw the drone on the map
# Function to draw the drone and its detection range on the map
def draw_drone(screen, drone_pos_cm):
    # Convert drone position from cm to pixels
    drone_pos_px = (drone_pos_cm[0] / 2.5, drone_pos_cm[1] / 2.5)
    drone_radius_px = 10 / 2.5  # 10 cm radius to pixels
    detection_range_px = 300 / 2.5  # 3 meters (300 cm) detection range to pixels

    # Draw the drone as a circle
    pygame.draw.circle(screen, (255, 0, 0), (int(drone_pos_px[0]), int(drone_pos_px[1])), int(drone_radius_px))

    # Draw detection range lines
    center_x, center_y = int(drone_pos_px[0]), int(drone_pos_px[1])

    # Forward (upward) detection line
    pygame.draw.line(screen, (0, 255, 0), (center_x, center_y), (center_x, center_y - detection_range_px))

    # Backward (downward) detection line
    pygame.draw.line(screen, (0, 255, 0), (center_x, center_y), (center_x, center_y + detection_range_px))

    # Right detection line
    pygame.draw.line(screen, (0, 255, 0), (center_x, center_y), (center_x + detection_range_px, center_y))

    # Left detection line
    pygame.draw.line(screen, (0, 255, 0), (center_x, center_y), (center_x - detection_range_px, center_y))


# Main function
if __name__ == "__main__":
    # Path to the image file (update this with your actual image path)
    image_path = "C:\\Users\dovy4\Desktop\אוניברסיטה גיבוי 3.3.2022\שנה ד סמסטר ב\רובוטים אוטונומיים\מטלה 1\EX1\Maps\p11.png"
    drone_position_cm = (300, 150)  # Example position

    display_map(image_path, drone_position_cm)
