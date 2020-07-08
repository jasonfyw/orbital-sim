import pygame
import math
import datetime
from astroquery.jplhorizons import Horizons
from astropy.time import Time

from environment import OrbitalSystem
import entities

class Simulation():
    def __init__(
        self, 
        dimensions = (1000, 1000), 
        scale = 300, 
        entity_scale = 10, 
        sim_rate = 1
    ):
        # dimensions: (width, height) of the window in pixels
        # scale: magnification ratio between AU and displayed pixels (default of 1AU = 300px)
        # entity_scale: additional magnification on the entities for visibility purposes
        # sim_rate: how many days pass in the simulation for every real-life second (default of 1 day per second)
        self.width, self.height = dimensions

        self.scale = scale
        self.entity_scale = entity_scale
        self.sim_rate = sim_rate 

        self.date = datetime.datetime.today()
        self.date_accumulator = 0

        self.solar_system = OrbitalSystem()

    def add_preset_solar_system(self):
        # add the sun, earth and mars with roughly accurate positioning and speed
        # mass in kg, position and diameter in AU
        planet_data = [(2e30, 9.5e-3), (3.3e23, 3.2e-5), (4.9e24, 8.1e-5), (6e24, 8.5e-5), (6.4e23, 4.5e-5)]
        id_list = ['Sun'] + [i for i in range(1, len(planet_data))]

        for i, id_ in enumerate(id_list):
            mass, diameter = planet_data[i]
            x, y, speed, angle = self.get_positioning(id_)

            self.solar_system.add_entity(position = (x, y), speed = speed, angle = angle, mass = mass, diameter = diameter)
        
    
    def get_positioning(self, nasaid):
        obj = Horizons(id = nasaid, location = '@sun', epochs = Time(self.date).jd, id_type = 'id').vectors()

        # get the components of position and velocity from JPL SSD 
        x, y = obj['x'], obj['y']
        vx, vy = obj['vx'], obj['vy']
        speed = math.hypot(vx, vy)

        # calculate angle of velocity by finding the tangent to the orbit
        # pygame specific: horizontally reflect the angle due to reversed y-axis
        angle = math.pi - ((2 * math.pi) - math.atan2(y, x))

        return x, y, speed, angle


    def update_date(self, delta_t):
        self.date_accumulator += 1 / ( (1000 / self.sim_rate) / delta_t )
        if self.date_accumulator >= 1:
            self.date += datetime.timedelta(days = self.date_accumulator)
            self.date_accumulator = 0

    def start(self):
        pygame.init()
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Orbital Simulation')
        self.paused = False

        # pass the sim_rate to each entity in the simulation
        for entity in self.solar_system.entities:
            entity.sim_rate = self.sim_rate

        font = pygame.font.SysFont('Courier New', 24)
        clock = pygame.time.Clock()
        running = True

        delta_t = 16

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    # pause simulation using spacebar
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
            
            if not self.paused:
                self.solar_system.update(delta_t)

                self.window.fill(self.solar_system.bg)
                date_display = font.render(self.date.strftime("%d %b %Y, %H:%M"), False, (200, 200, 200))
                self.window.blit(date_display, (0, 0))
                self.update_date(delta_t)

            for entity in self.solar_system.entities:
                x = int((entity.x * self.scale) + (self.width / 2))
                y = int((-entity.y * self.scale) + (self.height / 2)) # reflected across y-axis to compensate for pygame's reversed axes
                r = int(entity.diameter * self.scale * self.entity_scale / 2 )
                pygame.draw.circle(self.window, entity.colour, (x, y), r, 0)

            pygame.display.flip()
            delta_t = clock.tick(60)

def main():
    solar_system = Simulation((1000, 1000), sim_rate = 10)
    solar_system.add_preset_solar_system()
    solar_system.start()



if __name__ == "__main__":
    main()