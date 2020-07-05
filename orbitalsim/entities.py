import math


class Entity():
    def __init__(self, position, diameter, mass, speed, angle):
        self.x, self.y = position
        self.diameter = diameter
        self.mass = mass
        self.density = self.mass / (4/3 * math.pi * (self.diameter/2)**3)

        self.speed = speed
        self.angle = angle

    def move(self):
        self.x += math.sin(self.angle) * self.speed
        self.y -= math.sin(self.angle) * self.speed # subtract because of pygame's coord system

        



