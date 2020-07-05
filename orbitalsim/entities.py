import math
import constants as const

def add_vectors(vector1, vector2):
    # vectors are quantities with a magnitude and direction
    # add them by connecting them end-to-end to form one resulting vector
    # add the x and y components together to get a right-angled triangle with hypotenuse of the resulting vector's magnitude
    mag1, angle1 = vector1
    mag2, angle2 = vector2
    x = mag1 * math.sin(angle1) + mag2 * math.sin(angle2)
    y = mag1 * math.cos(angle1) + mag2 * math.cos(angle2)

    # use Pythagoras to find the magnitude of the resulting vector
    mag = math.hypot(x, y)
    # use inverse trig to find the angle of the right-angled triangle, take away from 90deg to get the resulting vecotr's angle
    # atan2 takes care of x = 0
    angle = (math.pi / 2) - math.atan2(y, x)

    return (mag, angle)

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

    def accelerate(self, acceleration):
        self.speed, self.angle = add_vectors((self.speed, self.angle), acceleration)

    def attract(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        theta = math.atan2(dx, dy)
        distance = math.hypot(dx, dy)

        # calculate attractive force due to gravity using Newton's law of universal gravitation:
        # F = G * m1 * m2 / r^2
        force = const.G * self.mass * other.mass / (distance ** 2)

        # accelerate both bodies towards each other by acceleration vector a = F/m, rearranged from Newton's second law
        self.accelerate((theta - (math.pi / 2), force / self.mass))
        other.accelerate((theta + (math.pi / 2), force / other.mass))



        



