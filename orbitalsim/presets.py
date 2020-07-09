from simulation import Simulation

"""
Parent class for presets – inherits from Simulation
"""
class Preset(Simulation):
    def __init__(
        self, 
        dimensions = (800, 800), 
        scale = -1, 
        entity_scale = 10, 
        sim_rate = 3,
        fullscreen = False
    ):
        super().__init__(dimensions, scale, entity_scale, sim_rate, fullscreen)

    def add_entities(self, observer_id):

        for id_ in self.entity_data.keys():
            mass = self.entity_data[id_]['m']
            diameter = self.entity_data[id_]['d']

            self.add_horizons_entity(
                entity_id = id_,
                observer_id = observer_id,
                mass = mass,
                diameter = diameter
            )

"""
Child classes for each preset
"""
class InnerSolarSystem(Preset):
    def __init__(self, 
        dimensions = (800, 800), 
        scale = -1, 
        entity_scale = 10, 
        sim_rate = 3,
        fullscreen = False
    ):
        super().__init__(dimensions, scale, entity_scale, sim_rate, fullscreen)

        self.entity_data = {
            'sun': {
                'm': 1.99e30,
                'd': 9.29e-3
            },
            '1': {
                'm': 3.30e23,
                'd': 3.26e-5
            },
            '2': {
                'm': 4.9e24,
                'd': 8.1e-5
            },
            '3': {
                'm': 6e24,
                'd': 8.5e-5
            },
            '4': {
                'm': 6.4e23,
                'd': 4.5e-5
            }
        }

        self.add_entities('sun')

class SolarSystem(Preset):
   def __init__(self, 
        dimensions = (800, 800), 
        scale = -1, 
        entity_scale = 10, 
        sim_rate = 3,
        fullscreen = False
    ):
        super().__init__(dimensions, scale, entity_scale, sim_rate, fullscreen)

        self.entity_data = {
            'sun': {
                'm': 1.99e30,
                'd': 9.29e-3
            },
            '1': {
                'm': 3.30e23,
                'd': 3.26e-5
            },
            '2': {
                'm': 4.9e24,
                'd': 8.1e-5
            },
            '3': {
                'm': 6e24,
                'd': 8.5e-5
            },
            '4': {
                'm': 6.4e23,
                'd': 4.5e-5
            },
            '5': {
                'm': 1.9e27,
                'd': 9.56e-4
            },
            '6': {
                'm': 5.7e26,
                'd': 8.05e-4
            },
            '7': {
                'm': 8.7e25,
                'd': 3.4e-4
            },
            '8': {
                'm': 1e26,
                'd': 3.31e-4
            }, 
            '9': {
                'm': 1.46e22,
                'd': 1.58e-5
            }
        }
        self.add_entities('sun')

class EarthMoon(Preset):
    def __init__(self, 
        dimensions = (800, 800), 
        scale = -1, 
        entity_scale = 1, 
        sim_rate = 3,
        fullscreen = False
    ):
        super().__init__(dimensions, scale, entity_scale, sim_rate, fullscreen)

        self.entity_data = {
            '3': {
                'm': 6e24,
                'd': 8.5e-5
            },
            '301': { 
                'm': 7.34e22,
                'd': 2.3e-5
            }
        }
        self.add_entities('3')
