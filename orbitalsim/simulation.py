import pygame
import math
import sys
import datetime
from astroquery.jplhorizons import Horizons
from astropy.time import Time

from orbitalsim.environment import OrbitalSystem

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

        # dx, dy: offset in px as a result of panning with arrow keys
        # offsetx, offsety: constants to centre (0,0) in the window
        self.dx = 0
        self.dy = 0
        self.offsetx = self.width / 2
        self.offsety = self.height / 2

        self.default_scale = scale
        self.scale = scale
        self.entity_scale = entity_scale
        self.sim_rate = sim_rate 

        self.date = datetime.datetime.today()
        self.date_accumulator = 0

        # initialise the Orbital System object
        self.solar_system = OrbitalSystem()

        self.fullscreen = fullscreen
        self.show_labels = True
        self.running = False
        self.paused = False

    """ 
    Viewmodel control
    """

    def scroll(self, dx = 0, dy = 0):
        # change offset to scroll/pan around the screen
        relative_scale = self.scale / self.default_scale
        self.dx += dx / relative_scale
        self.dy += dy / relative_scale

    def zoom(self, zoom):
        # adjust zoom level and zoom offset
        self.scale *= zoom

    def reset_zoom(self):
        # reset all viewmodel variables to default
        self.scale = self.default_scale
        self.dx = 0
        self.dy = 0

    def set_scale(self, max_a):
        # automatically calculate and set the scale based on the largest semi-major axis in the array of entities;
        # does nothing if scale manually set 
        if self.scale < 0:
            new_scale = min(self.width, self.height) / (2 * max_a) 
            self.scale = new_scale
            self.default_scale = new_scale

    def change_sim_rate(self, speed_ratio):
        self.sim_rate *= speed_ratio

    """
    Adding entities to simulation
    """

    def add_custom_entity(
        self,
        position,
        mass,
        speed = 0,
        angle = 0,
        diameter = 1e-5,
        e = 0,
        a = None,
        name = ''
    ):
        # position: tuple (x, y) describing the distance in AU from the centre of the system (0, 0)
        # speed: magnitude of initial velocity measured in AU/day
        # angle: angle of initial velocity given in rad
        # mass: measured in kg
        # diameter: measured in AU
        # (if applicable) e: eccentricity of the entity's orbit ranging from 0-1
        # (if applicable) a: semi-major axis of the entity's orbit measured in AU
        # (if applicable) name: str to display next to the entity when labels turned on
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

    def add_horizons_entity(self, entity_id, observer_id, mass, diameter = 1e-5):
        # entity_id, observer_id: the numerical ids designated by JPL SSD Horizons
        x, y, speed, angle, e, a, name = self.get_horizons_positioning(entity_id, observer_id)

        self.solar_system.add_entity(
            position = (x, y), 
            speed = speed, 
            angle = angle, 
            mass = mass, 
            diameter = diameter,
            e = e,
            a = a,
            name = name
        )
    
    def get_horizons_positioning(self, entity_id, observer_id):
        obj = Horizons(
                id = entity_id, 
                location = '@{}'.format(observer_id),
                epochs = Time(self.date).jd,
                id_type='id'
            )

        if not entity_id == observer_id:
            vectors = obj.vectors()
            elements = obj.elements()

            # get the eccentricity (e) and semimajor axis (a) 
            e = elements['e'].data[0]
            a = elements['a'].data[0]
            name = elements['targetname'].data[0].replace('Barycenter ', '')

            # get the components of position and velocity from JPL SSD 
            x, y = vectors['x'], vectors['y']
            vx, vy = vectors['vx'], vectors['vy']
            speed = math.hypot(vx, vy)

            # calculate angle of velocity by finding the tangent to the orbit
            # pygame specific: horizontally reflect the angle due to reversed y-axis
            angle = math.pi - ((2 * math.pi) - math.atan2(y, x))

            return x, y, speed, angle, e, a, name
        else:
            # special case for the central body of a system (e.g. the sun)
            # obj.elements() does not work for when entity_id and observer_id are the same
            name = obj.vectors()['targetname'].data[0].replace('Barycenter ', '')
            return 0, 0, 0, 0, 0, 0, name

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
            elif event.key == pygame.K_PERIOD:
                self.change_sim_rate(2)
            elif event.key == pygame.K_COMMA:
                self.change_sim_rate(0.5)
            elif event.key == pygame.K_l:
                self.show_labels = not self.show_labels
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
            self.offsetx = self.width / 2
            self.offsety = self.height / 2
        else:
            flag = 0
        self.window = pygame.display.set_mode((self.width, self.height), flag)
        pygame.display.set_caption('Orbital Simulation')
        delta_t = 16

        # pass the sim_rate to each entity in the simulation;
        # also calculate the largest semi-major axis and calculates scale if applicable
        semimajor_axes = []
        for entity in self.solar_system.entities:
            entity.sim_rate = self.sim_rate
            semimajor_axes.append(entity.a)
        self.set_scale(max(semimajor_axes))

        font = pygame.font.Font('orbitalsim/fonts/Inconsolata.ttf', 14)
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

            entity_labels = []
            for entity in self.solar_system.entities:
                entity.sim_rate = self.sim_rate
                # calculate pygame x, y coords 
                # this zooming stuff/scale is super sketchy yikes
                relative_scale = self.scale / self.default_scale
                x = int(relative_scale * ((self.scale * entity.x) + self.dx) + self.offsetx)
                y = int(relative_scale * ((self.scale * -entity.y) + self.dy) + self.offsety) # reflected across y-axis to compensate for pygame's reversed axes
                r = abs(int(entity.diameter * self.scale * self.entity_scale / 2 ))

                # additional stuff to make entities look nicer at large distances
                if r < 1 and self.scale > 300:
                    r = 2
                if entity.name == 'Sun (10)':
                    entity.colour = (243, 145, 50)
                    if r < 2:
                        r = 2

                pygame.draw.circle(self.window, entity.colour, (x, y), r, 0)

                label = font.render(entity.name, False, (180, 180, 180))
                entity_labels.append((label, (x + 3 + r, y + 3 + r)))

            if self.show_labels:
                for label in entity_labels:
                    text, position = label
                    self.window.blit(text, position)

            pygame.display.flip()
            delta_t = clock.tick(60)
