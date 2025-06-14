import math
from random import random

# Helper functions
def point_in_rect(px: int, py: int, rx: int, ry: int, rw: int, rh: int, rr:int) -> bool:
    """Check if a point (px, py) is inside a rectangle defined by (rx, ry, rw, rh) rotated by rr degrees."""
    # Translate point to rectangle's origin
    translated_x = px - rx
    translated_y = py - ry

    # Rotate point back to axis-aligned coordinates
    angle_rad = math.radians(-rr)
    rotated_x = translated_x * math.cos(angle_rad) - translated_y * math.sin(angle_rad)
    rotated_y = translated_x * math.sin(angle_rad) + translated_y * math.cos(angle_rad)

    # Check if the point is within the rectangle bounds
    return -rw/2 <= rotated_x <= rw/2 and -rh/2 <= rotated_y <= rh/2

# Basic entity class
class Entity:
    id: int
    type: str
    name: str

    # Positional attributes (updated every tick)
    x: int
    y: int
    heading: int
    speed: int

    def __init__(self, id: int, type: str, name: str, x: int, y: int, heading: int, speed: int):
        self.id = id
        self.type = type
        self.name = name
        self.x = x
        self.y = y
        self.heading = (360 - heading + 90) % 360
        self.speed = speed

    def tick_update(self):
        # Position
        self.x += self.speed * math.cos(math.radians(self.heading))
        self.y += self.speed * math.sin(math.radians(self.heading))

    def get_position(self):
        return (self.x, self.y, self.heading)

    def __str__(self):
        return f"{self.type} {self.name} at ({self.x}, {self.y}) heading {(360 + self.heading - 90) % 360}° with speed {self.speed}"

# Base class for all ships
class Ship(Entity):
    # Control attributes
    throttle: int              # How fast the ship is accelerating or decelerating (-100 to 100)
    steer: int                 # How much the ship is turning
    steer_target: int          # Target steer angle the ship is trying to reach

    # Technical attributes (dont change during gameplay)
    length: int
    width: int
    health_max: int                 # Maximum health of the ship
    speed_max: int
    speed_min: int
    speed_acceleration: int         # How fast the ship can reach its max speed
    speed_deceleration: int         # How fast the ship can slow down
    steer_max: int
    steer_speed: int                # How fast the ship can change its steer angle
    base_visibility: int            # Base visibility of the ship

    # Status attributes
    alive: bool
    health: int                     # Health of the ship, affects its ability to survive damage
    noise: int                      # Noise level of the ship, affects detection by enemies
    visibility: int

    def tick_update(self):
        # Position and heading
        if self.speed >= 0:
            self.x += (self.speed + (self.length * 1/6 * self.speed/self.speed_max)) * math.cos(math.radians(self.heading))
            self.y += (self.speed + (self.length * 1/6 * self.speed/self.speed_max)) * math.sin(math.radians(self.heading))
        else:
            self.x += (self.speed - (self.length * 1/6 * self.speed/self.speed_min)) * math.cos(math.radians(self.heading))
            self.y += (self.speed - (self.length * 1/6 * self.speed/self.speed_min)) * math.sin(math.radians(self.heading))
        
        self.heading = (360 + self.heading + self.steer) % 360

        if self.speed >= 0:
            self.x += -(self.length * 1/6 * self.speed/self.speed_max) * math.cos(math.radians(self.heading))
            self.y += -(self.length * 1/6 * self.speed/self.speed_max) * math.sin(math.radians(self.heading))
        else:
            self.x += (self.length * 1/6 * self.speed/self.speed_min) * math.cos(math.radians(self.heading))
            self.y += (self.length * 1/6 * self.speed/self.speed_min) * math.sin(math.radians(self.heading))
            
        # Throttle and speed
        if self.throttle > 0:
            if self.throttle > self.speed/self.speed_max * 100:
                self.speed += self.speed_acceleration * (1.5 - self.speed/self.speed_max)
            elif self.throttle < self.speed/self.speed_min * 100:
                self.speed += self.speed_deceleration * (1.5 - self.speed/self.speed_min)
        elif self.throttle < 0:
            if self.throttle < self.speed/self.speed_min * 100:
                self.speed -= self.speed_deceleration * (1.5 - self.speed/self.speed_min)
            elif self.throttle > self.speed/self.speed_max * 100:
                self.speed -= self.speed_acceleration * (1.5 - self.speed/self.speed_max)

        # Steer and heading
        if self.alive:
            if self.steer_target > self.steer:
                self.steer += self.steer_speed
                self.steer = min(self.steer, self.steer_target)
            elif self.steer_target < self.steer:
                self.steer -= self.steer_speed
                self.steer = max(self.steer, self.steer_target)

        # Visiblity and noise
        self.visibility = self.base_visibility * ((abs(self.speed) / self.speed_max) / 2 + 0.5)
        self.noise = 10 + abs(self.throttle)

        # Health
        if self.alive and self.health <= 0:
            self.alive = False
        if not self.alive:
            self.throttle = 0
    
    def take_damage(self, damage: int):
        self.health -= damage
        self.health = max(self.health, 0)
        
        if self.health <= 0:
            self.alive = False
            self.throttle = 0

# Class for the torpedoes fired by the player
class torpedo(Ship):
    # Technical attributes (dont change during gameplay)
    damage: int                     # Damage dealt by the torpedo when it hits a target

    # Control attributes
    targetAngle: int                # Angle towards which the torpedo is heading
    targetSpeed: int                # Speed at which the torpedo is moving



    def tick_update(self):
        if self.targetAngle - self.heading < -180 or self.targetAngle - self.heading > 180:
            if self.targetAngle - self.heading < -180:
                self.steer_target = ((self.targetAngle + 360) - self.heading)
            else:
                self.steer_target = ((self.targetAngle - 360) - self.heading)
        else:
            self.steer_target = (self.targetAngle - self.heading)
        if self.steer_target > self.steer_max:
            self.steer_target = self.steer_max
        elif self.steer_target < -self.steer_max:
            self.steer_target = -self.steer_max
        super().tick_update(self)

# Class for the player-controlled ship
class playerShip(Ship):
    # Control attributes
    periscope_angle: int            # Angle of the periscope, used for visual detection

    # Technical attributes (dont change during gameplay)
    battery_max: int                # Maximum battery level of the player ship
    battery_depletion_rate: int     # Rate at which the battery depletes, affects submerging and speed
    battery_recharge_rate: int      # Rate at which the battery recharges when surfaced
    underwater_speed_mult: float      # Multiplier for speed when underwater, affects how fast the player ship can move when submerged

    # Status attributes
    depth: str                      # Current depth of the player ship, affects visibility, noise and functionality, e.g., "surface", "periscope", "deep"
    battery: int                    # Battery level of the player ship, required for submerging
    periscope_active: bool          # Whether the periscope is currently active, affects visibility

    def tick_update(self):
        # Speed
        temp_speed = self.speed_max
        if self.depth != "surface":
            self.speed_max = self.speed_max * self.underwater_speed_mult

        # Battery
        if self.depth == "periscope" or self.depth == "deep":
            self.battery -= self.battery_depletion_rate
        elif self.depth == "surface":
            self.battery += self.battery_recharge_rate
        self.battery = max(0, min(self.battery, self.battery_max))
        if self.battery <= 0:
            self.depth = "surface"
            self.periscope_active = False

        super().tick_update(self)

        # Periscope# Visiblity and noise
        match self.depth:
            case "surface":
                self.visibility = self.base_visibility * ((abs(self.speed) / self.speed_max) / 2 + 0.5)
            case "periscope":
                if self.periscope_active:
                    self.visibility = self.base_visibility * ((abs(self.speed) / self.speed_max) / 2 + 0.5) * 0.2
                else:
                    self.visibility = self.base_visibility * ((abs(self.speed) / self.speed_max) / 2 + 0.5) * 0.01
            case "deep":
                self.visibility = 0
                self.noise = self.noise * 0.5  # Reduced noise when deep

        # Speed
        self.speed_max = temp_speed

# Base class for enemy ships
class enemyShip(Ship):
    # AI attributes
    ai_behaviour: str               # e.g., "careless", "safe", "aware", "combat"
    ai_combatMode: str              # e.g., "aggressive", "defensive", "evasive"
    visual_range: int               # Range at which the enemy can visually detect the player ship
    visual_skill: int               # Skill level of the enemy in visually detecting the player ship
    noise_range: int                # Range at which the enemy can detect the player ship based on noise
    noise_skill: int                # Skill level of the enemy in detecting the player ship based on noise

    # Technical attributes (dont change during gameplay)
    radio_range: int                # Range at which the enemy can share information with other enemy ships
    radio_skill: int                # Skill level of the enemy in sharing information with other enemy ships (accuracy and speed of information sharing)

    # Target attributes
        # Default navigation target
    objectivePosition: tuple[int, int]  # Final target position the enemy ship is trying to reach
        # Offensive
    spottedPlayer: bool             # Whether the enemy ship has spotted the player ship
    spottingAccuracy: int           # Accuracy of information about the player
    lastKnownPosition: tuple[int, int]  # Last known position of the player ship
    lastKnownTime: int              # Last time the enemy ship spotted the player ship
    lastKnownHeading: int           # Last known heading of the player ship
    lastKnownSpeed: int             # Last known speed of the player ship
        # Defensive
    spottedTorpedoes: list[torpedo] # List of torpedoes spotted by the enemy ship

# Class for depth charges used by enemy ships
class preDepthCharge:
    x: int                          # X offset of the depth charge from the ship
    y: int                          # Y offset of the depth charge from the ship
    target: Ship                    # Target ship the depth charge is aimed at
    time: int                       # Time until the depth charge is dropped

    def __init__(self, x: int, y: int, target: Ship, time: int):
        self.x = x
        self.y = y
        self.target = target
        self.time = time

    def tick_update(self):
        if self.time > 0:
            self.time -= 1

# Class for depth charges used by enemy ships
class depthCharge:
    x: int                          # X position of the depth charge
    y: int                          # Y position of the depth charge
    target: Ship                    # Target ship the depth charge is aimed at
    explosion_time: int             # Time until the depth charge explodes
    damage: int                     # Damage dealt by the depth charge
    splash_radius: int              # Splash radius of the depth charge explosion

    def __init__(self, x: int = 0, y: int = 0, target: Ship = None, explosion_time: int = 0, damage: int = 0, splash_radius: int = 0):
        self.x = x
        self.y = y
        self.target = target
        self.explosion_time = explosion_time
        self.damage = damage
        self.splash_radius = splash_radius

    def tick_update(self):
        if self.explosion_time > 0:
            self.explosion_time -= 1
        else:
            # Explode and deal damage to the target ship
            if self.target:
                distance = math.sqrt((self.x - self.target.x) ** 2 + (self.y - self.target.y) ** 2)
                if distance <= self.splash_radius:
                    self.target.take_damage(self.damage)

# Enemy ship capable of combat
class destroyer(enemyShip):
    # Combat attributes
        # Gun
    has_gun: bool                   # Whether the destroyer has a gun
    gun_range: int               # Range of the destroyer's weapons
    gun_damage: int              # Damage dealt by the destroyer's weapons
    gun_time_reload: int         # Time it takes to reload the destroyer's weapons
    gun_accuracy: int            # Accuracy of the destroyer's weapons
        # Depth charge
    has_depthCharge: bool          # Whether the destroyer has depth charges
    depthCharge_splash_radius: int # Splash radius of the destroyer's depth charges
    depthCharge_damage: int        # Damage dealt by the destroyer's depth charges
    depthCharge_time_reload: int   # Time it takes to reload the destroyer's depth charges
    depthCharge_burst_amount: int  # Number of depth charges in a burst
    depthCharge_burst_interval: int # Time between depth charges in a burst
    depthCharge_pattern: str       # Pattern of the depth charge attack, e.g., "behind", "sides", "all"
    depthCharge_pattern_size: int  # Distance from ship the charges are dropped
    depthCharge_explosion_time: int # Time it takes for the depth charge to explode after being dropped
        # Hedgehog
    has_hedgehog: bool              # Whether the destroyer has a hedgehog weapon
    hedgehog_range: int             # Range of the hedgehog weapon
    hedgehog_damage: int            # Damage dealt by the hedgehog weapon
    hedgehog_time_reload: int       # Time it takes to reload the hedgehog weapon
    hedgehog_burst_amount: int      # Number of hedgehog projectiles in a burst
    hedgehog_pattern_size: int      # Diameter of the attack pattern

    # Status attributes
    gun_time_lastFired: int      # Time when the last shot was fired
    depthCharge_time_lastDropped: int # Time when the last depth charge was dropped
    depthCharge_stack_dropping: list[preDepthCharge]  # List of depth charges left to drop
    depthCharge_stack_dropped: list[depthCharge]  # List of depth charges that have been dropped
    hedgehog_time_lastFired: int    # Time when the last hedgehog was fired

    def tick_update(self):
        super().tick_update(self)

        # Gun
        if self.has_gun and self.gun_time_lastFired > 0:
            self.gun_time_lastFired -= 1

        # Depth charge
        if self.has_depthCharge and self.depthCharge_time_lastDropped > 0:
            self.depthCharge_time_lastDropped -= 1
        
        if len(self.depthCharge_stack_dropping) > 0:
            for preCharge in self.depthCharge_stack_dropping:
                preCharge.tick_update()
                if preCharge.time <= 0:
                    self.stack_drop_depthCharge(preCharge)
                    self.depthCharge_stack_dropping.remove(preCharge)

        if len(self.depthCharge_stack_dropped) > 0:
            for charge in self.depthCharge_stack_dropped:
                charge.tick_update()
                if charge.explosion_time <= 0:
                    self.depthCharge_stack_dropped.remove(charge)

        # Hedgehog
        if self.has_hedgehog and self.hedgehog_time_lastFired > 0:
            self.hedgehog_time_lastFired -= 1

    # Gun functions
    def attack_gun(self, target: Ship):
        if not self.has_gun:
            return
        # Calculate distance to target
        distance = math.sqrt((self.x - target.x) ** 2 + (self.y - target.y) ** 2)
        if distance <= self.gun_range:
            # Calculate hit chance based on accuracy and distance
            if ((2 - distance / self.gun_range) * self.gun_accuracy) > random.randint(0, 100):
                # Hit the target
                target.take_damage(self.gun_damage)
            '''play sound?'''
        self.gun_time_lastFired = self.gun_time_reload  # Reset the reload time

    # Depth charge functions
    def attack_depth_charge(self, target: Ship):
        if not self.has_depthCharge:
            return
        match self.depthCharge_pattern:
            case "behind": # Drop depth charges behind the ships
                for i in range(self.depthCharge_burst_amount):
                    self.stack_add_depthCharge(0, -self.length/2 - self.depthCharge_pattern_size, i * self.depthCharge_burst_interval, target)
            case "sides": # Drop depth charges on both sides of the ship
                for i in range(self.depthCharge_burst_amount):
                    self.stack_add_depthCharge(-self.width/2 - self.depthCharge_pattern_size, 0, i * self.depthCharge_burst_interval, target)
                    self.stack_add_depthCharge(self.width/2 + self.depthCharge_pattern_size, 0, i * self.depthCharge_burst_interval, target)
            case "all": # Drop depth charges behind and both sides of the ship
                for i in range(self.depthCharge_burst_amount):
                    self.stack_add_depthCharge(0, -self.length/2 - self.depthCharge_pattern_size, i * self.depthCharge_burst_interval, target)
                    self.stack_add_depthCharge(-self.width/2 - self.depthCharge_pattern_size, 0, i * self.depthCharge_burst_interval, target)
                    self.stack_add_depthCharge(self.width/2 + self.depthCharge_pattern_size, 0, i * self.depthCharge_burst_interval, target)
        self.depthCharge_time_lastDropped = self.depthCharge_time_reload  # Reset the reload time

    def stack_add_depthCharge(self, xOff, yOff, delay, target: Ship):
        new_charge = preDepthCharge(x=xOff, y=yOff, target=target, time=delay)
        self.depthCharge_stack_dropping.append(new_charge)

    def stack_drop_depthCharge(self, preDepthCharge: preDepthCharge):
        offDis = math.sqrt(preDepthCharge.x ** 2 + preDepthCharge.y ** 2)
        offAngle = math.degrees(math.atan2(preDepthCharge.y, preDepthCharge.x))
        xOffset = self.x + offDis * math.cos(math.radians(self.heading) + offAngle)
        yOffset = self.y + offDis * math.sin(math.radians(self.heading) + offAngle)
        new_charge = depthCharge(xOffset, yOffset, preDepthCharge.target, self.depthCharge_explosion_time, self.depthCharge_damage, self.depthCharge_splash_radius)
        self.depthCharge_stack_dropped.append(new_charge)

    # Hedgehog functions
    def attack_hedgehog(self, target: Ship):
        if not self.has_hedgehog:
            return
        offMainDis = math.sqrt(0 ** 2 + (self.length/2) ** 2) + self.hedgehog_range
        xOffset = self.x + offMainDis * math.cos(math.radians(self.heading))
        yOffset = self.y + offMainDis * math.sin(math.radians(self.heading))
        offAngle = 360 / self.hedgehog_burst_amount
        for i in range(self.hedgehog_burst_amount):
            offSecDis = self.hedgehog_pattern_size/2
            xOffsetSec = xOffset + offSecDis * math.cos(math.radians(self.heading + offAngle * i))
            yOffsetSec = yOffset + offSecDis * math.sin(math.radians(self.heading + offAngle * i))
            if point_in_rect(xOffsetSec, yOffsetSec, target.x, target.y, target.width, target.length, target.heading):
                target.take_damage(self.hedgehog_damage)
        self.hedgehog_time_lastFired = self.hedgehog_time_reload  # Reset the reload time
        

# Enemy ship incapable of combat, objective for player to destroy
class transport(enemyShip):
    # Cargo attributes (???)
    cargo_type: str                 # Type of cargo the transport is carrying
    cargo_amount: int               # Amount of cargo the transport is carrying
    cargo_value: int                # Value of the cargo, affects score when destroyed