import pygame
import math
from environment import OrbitalSystem
import entities

class Simulation():
    def __init__(
        self, 
        dimensions = (1000, 1000), 
        scale = 300, 
        entity_scale = 20, 
        sim_rate = 1
    ):
        # dimensions: (width, height) of the window in pixels
        # scale: magnification ratio between AU and displayed pixels (default of 1AU = 300px)
        # entity_scale: additional magnification on the entities for visibility purposes
        # sim_rate: how many days pass in the simulation for every real-life second (default of 1 day per second)

        pygame.init()
        self.width, self.height = dimensions

        self.scale = scale
        self.entity_scale = entity_scale
        self.sim_rate = sim_rate 

        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Orbital Simulation')
        self.paused = False

        self.solar_system = OrbitalSystem()

    def add_preset_solar_system(self):
        # add the sun, earth and mars with roughly accurate positioning and speed
        # mass in kg, position and diameter in AU
        self.solar_system.add_entity(position = (0, 0), mass = 2e30, diameter = 9.46e-3) # the sun
        self.solar_system.add_entity(position = (0, 1), speed = 0.017298543, angle = math.pi / 2) # earth
        self.solar_system.add_entity(position = (0, 1.524), speed = 0.0138612, angle = math.pi / 2, diameter = 4.53215e-5, mass = 6.4e23) # mars

    def start(self):

        # pass the sim_rate to each entity in the simulation
        for entity in self.solar_system.entities:
            entity.sim_rate = self.sim_rate

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

            for entity in self.solar_system.entities:
                x = int((entity.x * self.scale) + (self.width / 2))
                y = int((entity.y * self.scale) + (self.height / 2))
                r = int(entity.diameter * self.scale * self.entity_scale / 2 )
                pygame.draw.circle(self.window, entity.colour, (x, y), r, 0)

            pygame.display.flip()
            delta_t = clock.tick(60)

def main():
    solar_system = Simulation((1000, 1000), sim_rate = 3)
    solar_system.add_preset_solar_system()
    solar_system.start()



if __name__ == "__main__":
    main()