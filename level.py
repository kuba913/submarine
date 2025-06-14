import ship

testEntity = ship.Entity(id=1, type="TestShip", name="Tester", x=100, y=200, heading=30, speed=5)

entityList = [testEntity] # List of ships in level

# Tick the level, updating all entities
def updateLevel(debug):
    if debug:
        print("Updating level with entities:")
        for entity in entityList:
            print(entity)
    for entity in entityList:
        entity.tick_update()