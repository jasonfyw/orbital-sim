import random
from entities import Entity

class OrbitalSystem():
    def __init__(self):
        self.entities = []

        self.bg = (0, 0, 0)

    def add_entity(self, **kargs):
        # diameter = kargs.get('diameter', 1.5e7)
        # mass = kargs.get('mass', 6e24)
        diameter = kargs.get('diameter', 10)
        mass = kargs.get('mass', 6e24)

        position = kargs.get('position', (diameter, diameter))

        entity = Entity(position, diameter, mass)
        entity.speed = kargs.get('speed', 0)
        entity.angle = kargs.get('angle', 0)

        self.entities.append(entity)

    def update(self):
        for i, entity in enumerate(self.entities):
            entity.move()
            entity.accelerate((0, 0))

            for entity2 in self.entities[i + 1:]:
                entity.attract(entity2)
