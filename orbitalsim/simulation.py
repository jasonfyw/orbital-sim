import pygame
import math
import sys
import datetime
from astroquery.jplhorizons import Horizons
from astropy.time import Time

from environment import OrbitalSystem

class Simulation():
    def __init__(
        self, 
        dimensions = (1000, 1000), 
        scale = -1, 
        entity_scale = 10, 
        sim_rate = 1
    ):
        # dimensions: (width, height) of the window in pixels
        # scale: magnification ratio between AU and displayed pixels (default of 1AU = 300px)
        # entity_scale: additional magnification on the entities for visibility purposes
        # sim_rate: how many days pass in the simulation for every real-life second (default of 1 day per second)
        self.width, self.height = dimensions
        self.offsetx = self.width / 2
        self.offsety = self.height / 2

        self.default_scale = scale
        self.scale = scale
        self.entity_scale = entity_scale
        self.sim_rate = sim_rate 

        self.date = datetime.datetime.today()
        self.date_accumulator = 0

        self.solar_system = OrbitalSystem()

        self.running = False

    def scroll(self, dx = 0, dy = 0):
        self.offsetx += dx
        self.offsety += dy

    def zoom(self, zoom):
        self.scale *= zoom

    def reset_zoom(self):
        self.scale = self.default_scale
        self.offsetx = self.width / 2
        self.offsety = self.height / 2

    def set_scale(self, max_a):
        if self.scale < 0:
            new_scale = min(self.width, self.height) / (2 * max_a) 
            self.scale = new_scale
            self.default_scale = new_scale


    def add_custom_entity(
        self,
        diameter,
        mass,
        position,
        speed = 0,
        angle = 0,
        e = 0,
        a = None
    ):
        if not a:
            x, y = position
            a = math.hypot(x, y)

        self.solar_system.add_entity(
            position = position, 
            speed = speed, 
            angle = angle, 
            mass = mass, 
            diameter = diameter,
            e = e,
            a = a
        )

    def add_horizons_entity(self, entity_id, observer_id, mass, diameter):
        x, y, speed, angle, e, a = self.get_horizons_positioning(entity_id, observer_id)
        self.solar_system.add_entity(
            position = (x, y), 
            speed = speed, 
            angle = angle, 
            mass = mass, 
            diameter = diameter,
            e = e,
            a = a
        )

    
    def get_horizons_positioning(self, entity_id, observer_id):
        if not entity_id == observer_id:
            obj = Horizons(
                id = entity_id, 
                location = '@{}'.format(observer_id),
                epochs = Time(self.date).jd,
                id_type='id'
            )
            vectors = obj.vectors()
            elements = obj.elements()

            # get the eccentricity (e) and semimajor axis (a) 
            e = elements['e'].data[0]
            a = elements['a'].data[0]

            # get the components of position and velocity from JPL SSD 
            x, y = vectors['x'], vectors['y']
            vx, vy = vectors['vx'], vectors['vy']
            speed = math.hypot(vx, vy)

            # calculate angle of velocity by finding the tangent to the orbit
            # pygame specific: horizontally reflect the angle due to reversed y-axis
            angle = math.pi - ((2 * math.pi) - math.atan2(y, x))

            return x, y, speed, angle, e, a
        else:
            return 0, 0, 0, 0, 0, 0


    def update_date(self, delta_t):
        self.date_accumulator += 1 / ( (1000 / self.sim_rate) / delta_t )
        if self.date_accumulator >= 1:
            self.date += datetime.timedelta(days = self.date_accumulator)
            self.date_accumulator = 0

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # pause simulation using spacebar
            if event.key == pygame.K_SPACE:
                self.paused = not self.paused
            elif event.key == pygame.K_LEFT:
                self.scroll(dx = 30)
            elif event.key == pygame.K_RIGHT:
                self.scroll(dx = -30)
            elif event.key == pygame.K_UP:
                self.scroll(dy = 30)
            elif event.key == pygame.K_DOWN:
                self.scroll(dy = -30)
            elif event.key == pygame.K_MINUS:
                self.zoom(0.5)
            elif event.key == pygame.K_EQUALS:
                self.zoom(2)
            elif event.key == pygame.K_r:
                self.reset_zoom()

    def start(self):
        pygame.init()
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Orbital Simulation')
        self.paused = False

        # pass the sim_rate to each entity in the simulation
        semimajor_axes = []
        for entity in self.solar_system.entities:
            entity.sim_rate = self.sim_rate
            semimajor_axes.append(entity.a)
        self.set_scale(max(semimajor_axes))

        font = pygame.font.SysFont('Courier New', 24)
        clock = pygame.time.Clock()
        self.running = True

        delta_t = 16

        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            
            if not self.paused:
                self.solar_system.update(delta_t)
                self.update_date(delta_t)

            self.window.fill(self.solar_system.bg)
            date_display = font.render(self.date.strftime("%d %b %Y, %H:%M"), False, (200, 200, 200))
            self.window.blit(date_display, (0, 0))

            for entity in self.solar_system.entities:
                x = int((entity.x * self.scale) + self.offsetx)
                y = int((-entity.y * self.scale) + self.offsety) # reflected across y-axis to compensate for pygame's reversed axes
                r = abs(int(entity.diameter * self.scale * self.entity_scale / 2 ))
                pygame.draw.circle(self.window, entity.colour, (x, y), r, 0)

            pygame.display.flip()
            delta_t = clock.tick(60)
