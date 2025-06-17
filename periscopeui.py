import pygame
import level
import ship
import math

def draw_ship(screen, location, size):
    width = size
    height = size // 3
    rect = pygame.Rect(location[0] - width // 2, location[1] - height // 2, width, height)
    pygame.draw.rect(screen, (0, 128, 255), rect)

def draw_periscope(screen, events, curr_ang, fov, my_ship):
    screen_width, screen_height = screen.get_size()

    # Calculate the periscope view rectangle
    periscope_rect = pygame.Rect(screen_width // 2 - 200, screen_height // 2 - 150, 400, 300)

    # Fill the periscope view area with a dark color
    pygame.draw.rect(screen, (50, 50, 50), periscope_rect)

    # Draw the field of view lines
    fov_angle_left = curr_ang - fov / 2
    fov_angle_right = curr_ang + fov / 2

    for sh in level.entityList:
        if isinstance(sh, ship.Entity) and sh.alive:
            # Check if the ship is within the field of view
            angle_to_ship = math.degrees(math.atan2(sh.y - my_ship.y, sh.x - my_ship.x))
            ship_x = screen_width // 2 + (sh.x - my_ship.x) * 10
            ship_y = screen_height // 2 - (sh.y - my_ship.y) * 10
            # Normalize the angle to be within 0-360 degrees
            angle_to_ship = (angle_to_ship + 360) % 360
            # Check if the ship is within the field of view
            if fov_angle_left <= angle_to_ship <= fov_angle_right:
                draw_ship(screen, (ship_x, ship_y), 20)
