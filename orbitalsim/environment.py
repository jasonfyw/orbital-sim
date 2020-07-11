from orbitalsim.entities import Entity

class OrbitalSystem():
    def __init__(self):
        self.entities = []

        self.bg = (0, 0, 0)

    def add_entity(
        self,
        diameter = 8.5e-5,
        mass = 6e24,
        position = (0, 0),
        speed = 0,
        angle = 0,
        e = 0,
        a = 1,
        name = ''
    ):
        entity = Entity(position, diameter, mass, e, a, name)
        entity.speed = speed
        entity.angle = angle

        self.entities.append(entity)

    def update(self, delta_t):
        for i, entity in enumerate(self.entities):
            entity.delta_t = delta_t
            entity.move()
            entity.accelerate((0, 0))

            for entity2 in self.entities[i + 1:]:
                entity.attract(entity2)
