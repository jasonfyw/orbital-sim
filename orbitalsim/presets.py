from simulation import Simulation


class InnerSolarSystem():
    def __init__(self, dimensions = (800, 800), sim_rate = 3):
        self.simulation = Simulation(dimensions, sim_rate = sim_rate)
        self.entity_data = {
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

        self.add_entities()

    def add_entities(self):
        # add the sun manually because Horizons elements() doesn't work on the sun
        self.simulation.add_custom_entity(
            diameter = 9.29e-3,
            mass = 1.99e30,
            position = (0, 0)
        )

        observer_id = 'sun'

        for id_ in self.entity_data.keys():
            mass = self.entity_data[id_]['m']
            diameter = self.entity_data[id_]['d']

            self.simulation.add_horizons_entity(
                entity_id = id_,
                observer_id = observer_id,
                mass = mass,
                diameter = diameter
            )

    def start(self):
        self.simulation.start()
