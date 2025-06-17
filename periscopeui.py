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
    pressed = pygame.key.get_pressed()  # Ensure key states are updated
    if pressed[pygame.K_LEFT]:
        level.playerShip.periscope_angle -= 15 * 1/60
    if pressed[pygame.K_RIGHT]:
        level.playerShip.periscope_angle += 15 * 1/60
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
            # Calculate the relative angle between periscope direction and ship
            rel_angle = angle_to_ship - curr_ang
            # Normalize to [-180, 180]
            rel_angle = (rel_angle + 180) % 360 - 180

            # Map relative angle to periscope view width
            half_fov = fov / 2
            if -half_fov <= rel_angle <= half_fov:
                # X position: center + (relative angle / half_fov) * (periscope_rect.width // 2)
                ship_x = periscope_rect.centerx + (rel_angle / half_fov) * (periscope_rect.width // 2)
                ship_y = periscope_rect.centery
                # Normalize the angle to be within 0-360 degrees
                angle_to_ship = (angle_to_ship + 360) % 360
                # Check if the ship is within the field of view
                if fov_angle_left <= angle_to_ship <= fov_angle_right:
                    distance = math.hypot(sh.x - my_ship.x, sh.y - my_ship.y)

                    min_size = 10
                    max_size = 80

                    min_dist = 10
                    max_dist = 1000
                    # Clamp distance
                    clamped_dist = max(min_dist, min(distance, max_dist))
                    # Inverse scale: closer ships are bigger
                    size = max_size - (clamped_dist - min_dist) / (max_dist - min_dist) * (max_size - min_size)
                    size = int(size)
                    draw_ship(screen, (ship_x, ship_y), size)
