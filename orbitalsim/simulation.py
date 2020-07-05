import pygame
import math
from environment import OrbitalSystem
import entities

class Viewmodel():
    def __init__(self, dimensions):
        self.width, self.height = dimensions



def main():
    width, height = 400, 400
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Orbital Simulation')

    solar_system = OrbitalSystem()

    solar_system.add_entity(position = (200, 200), mass = 2e30)
    solar_system.add_entity(position = (200, 250), speed = 2.2, angle = math.pi / 2)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        solar_system.update()
        window.fill((0, 0, 0))

        for entity in solar_system.entities:
            pygame.draw.circle(window, entity.colour, (int(entity.x), int(entity.y)), int(entity.diameter / 2), 0)

        # pygame.draw.circle(window, (255,255,255), (150, 100), 20, 0)
        # pygame.draw.circle(window, (255,255,255), (250, 200), 20, 0)
        # pygame.draw.circle(window, (255,255,255), (200, 250), 20, 0)
        



        pygame.display.flip()
        clock.tick(30)



if __name__ == "__main__":
    main()