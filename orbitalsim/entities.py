import math
from astropy.constants import G

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

"""
Main entity class
"""
class Entity():
    def __init__(self, position, diameter, mass, e = 0, a = 1, name = ''):
        # position: tuple (x, y) describing the distance in AU from the centre of the system (0, 0)
        # diameter: measured in AU
        # mass: measured in kg
        # speed: magnitude of initial velocity measured in AU/day
        # angle: angle of initial velocity given in rad
        # (if applicable) e: orbit eccentricity, 0-1
        # (if applicable) a: semi-major axis measured in AU
        self.x, self.y = position
        self.diameter = diameter
        self.mass = mass
        self.density = self.mass / (4/3 * math.pi * (self.diameter/2)**3)
        self.e = e
        self.a = a
        self.colour = (255, 255, 255)
        self.name = name

        self.speed = 0
        self.angle = 0

        # sim_rate: externally set, describes the number of days that pass in the simulation for every real life second (realtime is 1.2e-5)
        # delta_t: the time in ms between frames used to keep simulation rate consistent
        self.sim_rate = 1
        self.delta_t = 16

    def days_per_update(self):
        # returns the number of days that pass in a given interval delta_t
        return 1 / ( (1000 / self.sim_rate) / self.delta_t )

    """
    Physics calculations for movement
    """

    def move(self):
        # adjust speed for days past per frame
        # calculates next x, y position 
        dpu = self.days_per_update()
        self.x += math.sin(self.angle) * self.speed * dpu
        self.y -= math.cos(self.angle) * self.speed * dpu # subtract because of pygame's coord system

    def accelerate(self, acceleration):
        # adjusts magnitude of acceleration for days past per frame
        # combine apply acceleration to velocity vector
        acc_mag, acc_angle = acceleration
        acc_mag *= self.days_per_update()
        self.speed, self.angle = add_vectors((self.speed, self.angle), (acc_mag, acc_angle))

    def attract(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        theta = math.atan2(dy, dx)
        distance = math.hypot(dx, dy)

        # calculate attractive force due to gravity using Newton's law of universal gravitation:
        # F = G * m1 * m2 / r^2
        # for consistency, G = [AU^3 * kg^-1 * d^-2]
        force = G.to('AU3 / (kg d2)').value * self.mass * other.mass / (distance ** 2)

        # accelerate both bodies towards each other by acceleration vector a = F/m, rearranged from Newton's second law
        self.accelerate((force / self.mass, theta - (math.pi / 2)))
        other.accelerate((force / other.mass, theta + (math.pi / 2)))



        



