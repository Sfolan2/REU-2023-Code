# Sean Folan - UMass Amherst
# 2023 REU Big Data Privacy and Security Cal Poly Pomona

"""
Generates one ghost vehicle as defined in Bouchouia et al.'s files
"""

# Boilerplate CARLA import

import glob
import os
import sys
import time
import logging
import argparse

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import random

sys.path.append('./carla/Co-Simulation/Sumo')

from no_V2X_attacker_module import PositionAttacker

from sumo_integration.carla_simulation import CarlaSimulation

class Simulation():
    def __init__(self, args):
        self.args = args
        self.carla_simulation = CarlaSimulation(args.carla_host, args.carla_port, args.step_length)
        self.world = self.carla_simulation.world
        self.blueprint_library = self.world.get_blueprint_library()
        self.vehicle_bp = random.choice(self.blueprint_library.filter('vehicle.ford.ambulance'))
        self.attackers = [PositionAttacker()]

    def step(self):
        for attacker in self.attackers:
            attacker.perform_attack(self.carla_simulation,self.vehicle_bp)

    def loop(self):
        try:
            while True:
                self.step()
        except KeyboardInterrupt:
            logging.info('Cancelled by user.')
        finally:
            self.close()

    def close(self):
        print('******************************* closing all actors ********************************************')
        for actor in self.carla_simulation.world.get_actors().filter('vehicle.*.*'):
            actor.destroy()
        print('******************************* reset world ********************************************')
        settings = self.carla_simulation.world.get_settings()
        settings.synchronous_mode = False
        settings.fixed_delta_seconds = None     
        self.carla_simulation.world.apply_settings(settings)
        time.sleep(5)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument('--carla-host',
                           metavar='H',
                           default='127.0.0.1',
                           help='IP of the carla host server (default: 127.0.0.1)')
    argparser.add_argument('--carla-port',
                           metavar='P',
                           default=2000,
                           type=int,
                           help='TCP port to listen to (default: 2000)')
    argparser.add_argument('--step-length',
                           default=0.05,
                           type=float,
                           help='set fixed delta seconds (default: 0.05s)')
    arguments = argparser.parse_args()
    simulation = Simulation(arguments)
    simulation.loop()




