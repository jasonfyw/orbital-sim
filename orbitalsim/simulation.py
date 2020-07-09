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
        dimensions = (800, 800), 
        scale = -1, 
        entity_scale = 10, 
        sim_rate = 3,
        fullscreen = False
    ):
        # dimensions: (width, height) of the window in pixels
        # scale: magnification ratio between AU and displayed pixels (default of -1: automatically calculated by self.set_scale())
        # entity_scale: additional magnification on the entities for visibility purposes
        # sim_rate: how many days pass in the simulation for every real-life second (default of 1 day per second)
        # fullscreen: boolean – if true, automatically overrides dimensions
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

        self.fullscreen = fullscreen
        self.running = False

    """ 
    Viewmodel control
    """

    def scroll(self, dx = 0, dy = 0):
        self.offsetx += dx
        self.offsety += dy

    def zoom(self, zoom):
        self.scale *= zoom
        self.offsetx *= zoom
        self.offsety *= zoom

    def reset_zoom(self):
        self.scale = self.default_scale
        self.offsetx = self.width / 2
        self.offsety = self.height / 2

    def set_scale(self, max_a):
        # automatically calculate and set the scale based on the largest semi-major axis in the array of entities;
        # does nothing if scale manually set 
        if self.scale < 0:
            new_scale = min(self.width, self.height) / (2 * max_a) 
            self.scale = new_scale
            self.default_scale = new_scale

    """
    Adding entities to simulation
    """

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
        # diameter: measured in AU
        # mass: measured in kg
        # position: tuple (x, y) describing the distance in AU from the centre of the system (0, 0)
        # speed: magnitude of initial velocity measured in AU/day
        # angle: angle of initial velocity given in rad
        # (if applicable) e: eccentricity of the entity's orbit ranging from 0-1
        # (if applicable) a: semi-major axis of the entity's orbit measured in AU
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
        # entity_id, observer_id: the numerical ids designated by JPL SSD Horizons
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
            # special case for the central body of a system (e.g. the sun)
            # obj.elements() does not work for when entity_id and observer_id are the same
            return 0, 0, 0, 0, 0, 0

    """
    Simulation functions
    """

    def update_date(self, delta_t):
        # calculate the number of days past in the simulation since last frame
        # update simulation date when accumulator overflows
        # no functional purpose, used for display
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
                self.zoom(0.667)
            elif event.key == pygame.K_EQUALS:
                self.zoom(1.5)
            elif event.key == pygame.K_r:
                self.reset_zoom()
            elif event.key == pygame.K_q:
                self.running = False
                pygame.quit()
                sys.exit()

    """
    Main simulation function
    """

    def start(self):

        """ 
        Setup 
        """
        pygame.init()

        if self.fullscreen:
            flag = pygame.FULLSCREEN

            display_info = pygame.display.Info()
            self.width = display_info.current_w
            self.height = display_info.current_h
        else:
            flag = 0

        self.window = pygame.display.set_mode((self.width, self.height), flag)
        pygame.display.set_caption('Orbital Simulation')
        self.paused = False
        delta_t = 16

        # pass the sim_rate to each entity in the simulation;
        # also calculate the largest semi-major axis and calculates scale if applicable
        semimajor_axes = []
        for entity in self.solar_system.entities:
            entity.sim_rate = self.sim_rate
            semimajor_axes.append(entity.a)
        self.set_scale(max(semimajor_axes))

        font = pygame.font.SysFont('Courier New', 24)
        clock = pygame.time.Clock()
        self.running = True
        

        """
        Simulation loop
        """
        while self.running:
            # handle events
            for event in pygame.event.get():
                self.handle_event(event)
            
            # update frame
            if not self.paused:
                self.solar_system.update(delta_t)
                self.update_date(delta_t)

            # render frame
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
