class PositionAttacker(Attacker):
    """
    Repeatedly sends a CAM at the same Waypoint

    We initialize with target_vehicle_cams and an x and y. Then we create CAMs
    from that x and y position to all of the previous vehicles that have been
    sent CAMs
    """
    def __init__(self, x, y):
        self.extra_args = {'sender_pos_x': x, 'sender_pos_y': y}

    def perform_attack(self, target_vehicle_cams):
        cam_list = []
        for prev_cam in target_vehicle_cams:
            cam_list.append(CAM(prev_cam, self.extra_args).cam_dict)
        return cam_list