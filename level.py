import ship

testEntity = ship.Entity(id=1, type="TestShip", name="Tester", x=100, y=200, heading=30, speed=5)

entityList = [testEntity] # List of ships in level

# Tick the level, updating all entities
def updateLevel(debug):
    for entity in entityList:
        entity.tick_update()
        if debug:
            print(entity)