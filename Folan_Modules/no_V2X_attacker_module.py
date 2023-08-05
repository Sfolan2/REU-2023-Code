# Sean Folan - UMass Amherst
# 2023 REU Big Data Privacy and Security Cal Poly Pomona

"""
Primarily for testing, I want to see how the ghost vehicles behave without the
full artery/V2X components. This file is essentially attacker_module.py without
all of the SUMO/Artery stuff.
"""

import carla

class Attacker(object):
    def __init__(self):
        self.ghosts = []

    def perform_attack(self):
        pass

    def kill_ghosts(self):
        for ghost_id in self.ghosts:
            carla.destroy(ghost_id)
        self.ghosts = []

    def create_ghost_vehicle(self, carla_client, ghost_vehicle_bp, new_location, new_control):
        if len(self.ghosts) == 0:
            self.spawn_ghost(carla_client, ghost_vehicle_bp, new_location, new_control)

    def spawn_ghost(self, carla_client, ghost_vehicle_bp, location, ghost_control):
        spawned_actor_id = carla_client.spawn_actor(ghost_vehicle_bp, location)
        if spawned_actor_id<0 :
            return
        actor=carla_client.world.get_actor(spawned_actor_id)
        if actor : 
            actor.set_autopilot(False)
            actor.set_simulate_physics(enabled=False)  
            self.ghosts.append(actor.id)
            actor.apply_control(ghost_control)


class PositionAttacker(Attacker):
    def perform_attack(self, carla_var, ghost_vehicle_bp):
        new_location,ghost_control = self.computeNewPositionAndControl(carla_var)
        self.create_ghost_vehicle(carla_var,ghost_vehicle_bp,new_location,ghost_control)
       

    def computeNewPositionAndControl(self,carla_client):
        spawn_points = carla_client.world.get_map().get_spawn_points()
        spawn_location = spawn_points[0]
        new_location = carla.Transform(carla.Location(spawn_location.location.x,spawn_location.location.y,-24), carla.Rotation(0,0,0))
        control = carla.VehicleControl()
        return new_location, control