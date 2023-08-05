# Sean Folan - UMass Amherst
# Cal Poly Pomona Big Data Security and Privacy REU

'''
Implement attacks through an injection of V2X messages between
Artery and CARLA
'''

import carla

import numpy as np

class CAM(object):
    def __init__(self, prev_cam, extra_args):
        """
        The idea is that an attacker could be listening to the CAMs and get some default
        values that match a previous cam which would look more suspicious. Then we can just
        change things we want to change like the location and speed.
        """ 
        self.cam_dict = prev_cam
        for arg in extra_args:
            self.cam_dict[arg] = extra_args[arg]


class Attacker(object):
    def __init__(self):
        pass

    def perform_attack(self):
        pass


class PositionAttacker(Attacker):
    """
    Repeatedly sends a CAM at the same Waypoint

    We initialize with target_vehicle_cams and a waypoint. Then we create CAMs
    from that x and y position to all of the previous vehicles that have been
    sent CAMs
    """
    def __init__(self, waypoint):
        self.location = waypoint.transform.location
        self.extra_args = {'sender_pos_x': self.location.x, 'sender_pos_y': self.location.y}

    def perform_attack(self, target_vehicle_cams):
        cam_list = []
        for prev_cam in target_vehicle_cams:
            cam_list.append(CAM(prev_cam, self.extra_args).cam_dict)
        return cam_list


class ConstantOffsetAttacker(Attacker):
    """
    Takes a normal vehicle and sends a CAM as
    if there was a vehicle x meters ahead of the
    vehicle on the road
    """
    def __init__(self, offset_vehicle, offset_distance):
        self.offset_vehicle = offset_vehicle
        self.offset_distance = offset_distance

    def perform_attack(self, target_vehicle_cams):
        cam_list = []
        location = self.offset_vehicle.get_location()
        unit_velocity = self.offset_vehicle.get_velocity() # Make sure z-vector is neglible or fix
        if unit_velocity.length() > 0:
            unit_velocity.make_unit_vector()
        else:
            unit_velocity = carla.Vector3D(0,0,0)
        x_comp = location.x + (self.offset_distance * unit_velocity.x)
        y_comp = location.y + (self.offset_distance * unit_velocity.y)
        extra_args = {'sender_pos_x': x_comp, 'sender_pos_y': y_comp}
        for prev_cam in target_vehicle_cams:
            cam_list.append(CAM(prev_cam, extra_args).cam_dict)
        return cam_list
    
class RandomOffsetAttacker(ConstantOffsetAttacker):
    def perform_attack(self, target_vehicle_cams):
        cam_list = []
        rand_multiplier = np.random.normal(1, .5)
        location = self.offset_vehicle.get_location()
        unit_velocity = self.offset_vehicle.get_velocity()# Make sure z-vector is neglible or fix
        if unit_velocity.length() > 0:
            unit_velocity.make_unit_vector()
        else:
            unit_velocity = carla.Vector3D(0,0,0)
        x_comp = location.x + (rand_multiplier * (self.offset_distance * unit_velocity.x))
        y_comp = location.y + (rand_multiplier * (self.offset_distance * unit_velocity.y))
        extra_args = {'sender_pos_x': x_comp, 'sender_pos_y': y_comp}
        for prev_cam in target_vehicle_cams:
            cam_list.append(CAM(prev_cam, extra_args).cam_dict)
        return cam_list
    
class DENM(object):
    def __init__(self, prev_denm, extra_args):
        """
        Blueprint for DENM
        """ 
        self.denm_dict = prev_denm
        for arg in extra_args:
            self.denm_dict[arg] = extra_args[arg]

class TrafficJamAttack(Attacker):
    # We need to make two messages
    # TrafficJamAhead
    def __init__(self, prev_denm, lat, long): 
        self.extra_args_ahead = {
            'Validity Duration': 60,
            'Relevance Distance': 4,
            'Relevance Traffic Detection': 1,
            'Cause Code': 1,
            'Sub Cause Code':0,
            'sender_pos_x':lat,
            'sender_pos_y':long}
        self.denm_ahead = DENM(prev_denm, self.extra_args_ahead)

        self.extra_args_end = {
            'Validity Duration': 20,
            'Relevance Distance': 4,
            'Relevance Traffic Detection': 1,
            'Cause Code': 27,
            'Sub Cause Code':0,
            'sender_pos_x':lat,
            'sender_pos_y':long}
        self.denm_end = DENM(prev_denm, self.extra_args_end)

    def perform_attack(self):
        return [self.denm_ahead.denm_dict, self.denm_end.denm_dict]

class EmergencyBrakingAttack(Attacker):
    def __init__(self, prev_denm, lat, long): 
        self.extra_args = {
            'Validity Duration': 2,
            'Relevance Distance': 3,
            'Cause Code':99,
            'Sub Cause Code':1,
            'sender_pos_x':lat,
            'sender_pos_y':long}
        self.denm = DENM(prev_denm, self.extra_args)

    def perform_attack(self):
        return [self.denm.denm_dict]

class TractionLossAttack(Attacker):
    def __init__(self, prev_denm, lat, long): 
        self.extra_args = {
            'Validity Duration': 600,
            'Relevance Distance': 1,
            'Cause Code':6,
            'Sub Cause Code':0,
            'sender_pos_x':lat,
            'sender_pos_y':long}
        self.denm = DENM(prev_denm, self.extra_args)

    def perform_attack(self):
        return [self.denm.denm_dict]


