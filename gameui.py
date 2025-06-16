import pygame
import os
import level
from settings import SCREEN_SCALING_RATIO
from enum import Enum

class InputType(Enum):
    RADAR = "radar"
    STEER_LEFT = "steer_left"
    STEER_RIGHT = "steer_right"
    TORPEDO1 = "torpedo1"
    TORPEDO2 = "torpedo2"
    PERISCOPE = "periscope"
    THROTTLE_UP = "throttle_up"
    THROTTLE_DOWN = "throttle_down"
    NONE = "none"

class UIScreen(Enum):
    PANEL = "panel"
    TOPDOWN = "topdown"
    PERISCOPE = "periscope"

class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vec2(self.x / scalar, self.y / scalar)

    def __repr__(self):
        return f"Vec2({self.x}, {self.y})"

    def to_tuple(self):
        return (self.x, self.y)

class BoundingBox2D:
    def __init__(self, top_left: Vec2, bottom_right: Vec2):
        self.top_left = top_left
        self.bottom_right = bottom_right

    def contains(self, point: Vec2):
        return (self.top_left.x <= point.x <= self.bottom_right.x and
                self.top_left.y <= point.y <= self.bottom_right.y)

class Throttler:
    def __init__(self):
        self.value = 0

    def up(self):
        if self.value >= 1:
            return
        self.value += 1

    def down(self):
        if self.value <= -1:
            return
        self.value -= 1
    
    def reset(self):
        self.value = 0

    def get_value(self):
        return self.value

class Wheel:
    def __init__(self):
        self.value = 0

    def right(self):
        if self.value >= 1:
            return
        self.value += 1

    def left(self):
        if self.value <= -1:
            return
        self.value -= 1
    
    def reset(self):
        self.value = 0

    def get_value(self):
        return self.value


current_screen = UIScreen.PANEL
img_location_radar = BoundingBox2D(Vec2(820, 1300) * SCREEN_SCALING_RATIO, Vec2(1080, 1550) * SCREEN_SCALING_RATIO)
img_location_steer_left = BoundingBox2D(Vec2(330, 1060) * SCREEN_SCALING_RATIO, Vec2(475, 1300) * SCREEN_SCALING_RATIO)
img_location_steer_right = BoundingBox2D(Vec2(520, 1060) * SCREEN_SCALING_RATIO, Vec2(650, 1300) * SCREEN_SCALING_RATIO)
img_location_torpedo1 = BoundingBox2D(Vec2(160, 880) * SCREEN_SCALING_RATIO, Vec2(300, 1160) * SCREEN_SCALING_RATIO)
img_location_torpedo2 = BoundingBox2D(Vec2(694, 908) * SCREEN_SCALING_RATIO, Vec2(800, 1190) * SCREEN_SCALING_RATIO)
img_location_periscope = BoundingBox2D(Vec2(900, 100) * SCREEN_SCALING_RATIO, Vec2(1040, 586) * SCREEN_SCALING_RATIO)
img_locaton_throttle_up = BoundingBox2D(Vec2(894, 1020) * SCREEN_SCALING_RATIO, Vec2(948, 1090) * SCREEN_SCALING_RATIO)
img_location_throttle_down = BoundingBox2D(Vec2(894, 1100) * SCREEN_SCALING_RATIO, Vec2(948, 1180) * SCREEN_SCALING_RATIO)

bg_img = pygame.image.load(os.path.join("assets", "img", "submarine_main_bg.png"))
bg_img = pygame.transform.scale_by(bg_img, SCREEN_SCALING_RATIO)
throttler_img = pygame.image.load(os.path.join("assets", "img", "throttler.png"))
throttler_img = pygame.transform.scale_by(throttler_img, SCREEN_SCALING_RATIO / 2)
wheel_img = pygame.image.load(os.path.join("assets", "img", "wheel.png"))
wheel_img = pygame.transform.scale_by(wheel_img, SCREEN_SCALING_RATIO)

wheel_size = wheel_img.get_size()
wheel_size = Vec2(wheel_size[0], wheel_size[1])
img_location_wheel = Vec2(494, 1180) * SCREEN_SCALING_RATIO

throttler_size = throttler_img.get_size()
throttler_size = Vec2(throttler_size[0], throttler_size[1])
img_location_throttler = Vec2(922, 1090) * SCREEN_SCALING_RATIO - throttler_size / 2

throttler = Throttler()
wheel = Wheel()

def switch_screen(new_screen):
    """Switch the current UI screen."""
    global current_screen
    current_screen = new_screen

def draw_bg(screen):
    """Draw the background image on the screen."""
    screen.blit(bg_img, (0, 0))

def check_input(mouse_pos):
    """Check if the mouse position is within any clickable UI elements."""
    pos = Vec2(mouse_pos[0], mouse_pos[1])
    if img_location_radar.contains(pos):
        return InputType.RADAR
    elif img_location_steer_left.contains(pos):
        return InputType.STEER_LEFT
    elif img_location_steer_right.contains(pos):
        return InputType.STEER_RIGHT
    elif img_location_torpedo1.contains(pos):
        return InputType.TORPEDO1
    elif img_location_torpedo2.contains(pos):
        return InputType.TORPEDO2
    elif img_location_periscope.contains(pos):
        return InputType.PERISCOPE
    elif img_locaton_throttle_up.contains(pos):
        return InputType.THROTTLE_UP
    elif img_location_throttle_down.contains(pos):
        return InputType.THROTTLE_DOWN
    else:
        return InputType.NONE

def draw_wheel(screen):
    """Draw the steering wheel image on the screen."""
    rotated_wheel_img = pygame.transform.rotate(wheel_img, -wheel.get_value() * 30)  # Rotate based on wheel value
    wheel_rect = rotated_wheel_img.get_rect(center=img_location_wheel.to_tuple())
    screen.blit(rotated_wheel_img, wheel_rect)

def draw_throttler(screen):
    """Draw the throttler image on the screen."""
    offset = throttler.get_value() * 20 * SCREEN_SCALING_RATIO  # Adjust the offset based on throttler value
    location = img_location_throttler + Vec2(0, -offset)
    screen.blit(throttler_img, location.to_tuple())

def handle_panel_ui(screen):
    draw_bg(screen)
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            input_type = check_input(mouse_pos)
            if input_type == InputType.THROTTLE_UP:
                throttler.up()
                #level.playerShip.throttle = min(level.playerShip.throttle+10, 100)
            elif input_type == InputType.THROTTLE_DOWN:
                throttler.down()
                #level.playerShip.throttle = max(level.playerShip.throttle-10, -100)
            elif input_type == InputType.STEER_LEFT:
                wheel.left()
                level.playerShip.steer_target = min(level.playerShip.steer_target+2, level.playerShip.steer_max)
            elif input_type == InputType.STEER_RIGHT:
                wheel.right()
                level.playerShip.steer_target = max(level.playerShip.steer_target-2, -level.playerShip.steer_max)
            elif input_type == InputType.RADAR:
                switch_screen(UIScreen.TOPDOWN)
            elif input_type == InputType.TORPEDO1:
                level.playerShip.attack_torpedo(0)
                print("Torpedo 1 clicked")
            elif input_type == InputType.TORPEDO2:
                print("Torpedo 2 clicked")
            elif input_type == InputType.PERISCOPE:
                print("Periscope clicked")

    draw_wheel(screen)
    draw_throttler(screen)

# TODO move these to ship.py or similar
# How fast the ship throttles up/down when the lever is up/down
throttle_per_sec = 10  # Throttle change per second
def update_ship_throttle(coefficient):
    # ! Hardcoded 60 FPS, may need to change to delta time.
    if coefficient == 0:
        # Slowly return throttle to zero
        if level.playerShip.throttle > 0:
            level.playerShip.throttle -= throttle_per_sec * 1/60
            if level.playerShip.throttle < 0:
                level.playerShip.throttle = 0
        elif level.playerShip.throttle < 0:
            level.playerShip.throttle += throttle_per_sec * 1/60
            if level.playerShip.throttle > 0:
                level.playerShip.throttle = 0
    else:
        level.playerShip.throttle += coefficient * throttle_per_sec * 1/60

    level.playerShip.throttle = max(min(level.playerShip.throttle, 100), -100)

# How fast does the ship turn left/right when the wheel is turned left/right
steer_per_sec = 1  # Steering change per second
def update_ship_steering(coefficient):
    # ! Hardcoded 60 FPS, may need to change to delta time.
    level.playerShip.steer_target += coefficient * 1 * 1/60
    level.playerShip.steer_target = max(min(level.playerShip.steer_target, level.playerShip.steer_max), -level.playerShip.steer_max)
    

def draw_ui(screen):
    screen.fill((0,0,0))
    global current_screen
    update_ship_throttle(throttler.get_value())
    #update_ship_steering(wheel.get_value())
    match current_screen:
        case UIScreen.PANEL:
            handle_panel_ui(screen)
        case UIScreen.TOPDOWN:
            level.debugDrawLevel(screen)
        
        

