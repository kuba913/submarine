import math
import pygame
import ship

entityList = [] # List of ships in level

playerShip = ship.playerShip(len(entityList), x=0, y=0, heading=0)
ship.transport(len(entityList), 50, 200, 90, "cargo", 1, 1)
#ship.Entity(len(entityList), type="TestShip", name="Tester", x=0, y=0, heading=0, speed=5)

# Tick the level, updating all entities
def updateLevel(debug):
    if debug:
        print("Updating level with entities:")
        for entity in entityList:
            print(entity)
    for entity in entityList:
        entity.tick_update()

def debugDrawLevel(screen):
    for entity in entityList:
        match type(entity):
            case ship.Entity:
                pygame.draw.circle(screen, (255, 255, 255), (screen.get_width()/2 + entity.x, screen.get_height()/2 - entity.y), 2)
            case ship.playerShip | ship.destroyer | ship.transport | ship.torpedo:
                if entity.alive:
                    pLen = math.sqrt((entity.width/2) ** 2 + (entity.length/2) ** 2)

                    p1x = screen.get_width()/2 + (entity.x + pLen * math.cos(math.atan2(entity.width/2, entity.length/2) + math.radians(entity.heading)))
                    p1y = screen.get_height()/2 - (entity.y + pLen * math.sin(math.atan2(entity.width/2, entity.length/2) + math.radians(entity.heading)))

                    p2x = screen.get_width()/2 + (entity.x + pLen * math.cos(math.atan2(-entity.width/2, entity.length/2) + math.radians(entity.heading)))
                    p2y = screen.get_height()/2 - (entity.y + pLen * math.sin(math.atan2(-entity.width/2, entity.length/2) + math.radians(entity.heading)))

                    p3x = screen.get_width()/2 + (entity.x + pLen * math.cos(math.atan2(-entity.width/2, -entity.length/2) + math.radians(entity.heading)))
                    p3y = screen.get_height()/2 - (entity.y + pLen * math.sin(math.atan2(-entity.width/2, -entity.length/2) + math.radians(entity.heading)))

                    p4x = screen.get_width()/2 + (entity.x + pLen * math.cos(math.atan2(entity.width/2, -entity.length/2) + math.radians(entity.heading)))
                    p4y = screen.get_height()/2 - (entity.y + pLen * math.sin(math.atan2(entity.width/2, -entity.length/2) + math.radians(entity.heading)))

                    pygame.draw.polygon(screen, (255, 255, 255), [[p1x, p1y], [p2x, p2y], [p3x, p3y], [p4x, p4y]])