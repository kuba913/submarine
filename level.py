import math
import pygame
import ship
import pickle

global entityList
global playerShip

entityList = [] # List of ships in level

# Used in ship.destoryerai_combat_behavior
def get_player():
    for entity in entityList:
        if entity.type == "playerShip":
            return entity
    return None

# Tick the level, updating all entities
def updateLevel(debug):
    if debug:
        print("Updating level with entities:")
        for entity in entityList:
            print(entity)
            print("health: ", entity.health)
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

# Save/Load

def saveLevel(entityList, saveName):
    pickle.dump(entityList, open(saveName, "wb"))

def loadSave(saveName):
    global entityList
    global playerShip
    entityList = pickle.load(open(saveName, "rb"))
    playerShip = get_player()