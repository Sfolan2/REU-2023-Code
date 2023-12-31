"""
Script to inject attacks in recieved artery messages in python
"""
# ==================================================================================================
# -- imports ---------------------------------------------------------------------------------------
# ==================================================================================================
import carla
import time
import math

from sumo_integration.bridge_helper import BridgeHelper  # pylint: disable=wrong-import-position


class Painter(object):

    def __init__(self,attacker_color=carla.Color(255,0,0),victim_color=carla.Color(0,255,0),ghost_color=carla.Color(75,0,130),detection_color=carla.Color(0,0,120),freq=0.5):
        self.attacker_color = attacker_color
        self.victim_color = victim_color
        self.ghost_color=ghost_color
        self.detection_color = detection_color
        self.freq= freq
        self.vehicle_box_dims=carla.Vector3D(1,0.5,1)
        self.detection_box_dims=carla.Vector3D(0.05,0.05,0.05)

    def color_agents(self,synchronization,victimes,attackers,detections):
        coloring_brush = synchronization.carla.world.debug
        # self.colorAttackersAndGhosts(coloring_brush,synchronization,attackers)
        self.colorVictims(coloring_brush,synchronization,victimes)
        # self.colorDetections(coloring_brush,synchronization,detections)

    def color_communication(self,synchronization,cam):
        coloring_brush = synchronization.carla.world.debug
        if cam.get('sender_pos_x') and cam.get('receiver_pos_x'):
                coloring_brush.draw_arrow(
                carla.Location(cam['sender_pos_x'],cam['sender_pos_y'],20), #temp change
                carla.Location(cam['receiver_pos_x'],cam['receiver_pos_y'],20),thickness=0.2,life_time=self.freq,color=carla.Color(255,0,0))


    def colorAttackersAndGhosts(self,coloring_brush,synchronization,attackers):
            for attacker in attackers:
                if attacker.is_ready(synchronization.sumo2carla_ids):
                    actor=synchronization.carla.world.get_actor(attacker.carla_id)
                    coloring_brush.draw_box(carla.BoundingBox(actor.get_transform().location,self.vehicle_box_dims),actor.get_transform().rotation, 3, self.attacker_color,self.freq)
                    if len(attacker.ghosts)!=0:
                        actor=synchronization.carla.get_actor(attacker.ghosts[0])
                        coloring_brush.draw_box(carla.BoundingBox(actor.get_transform().location,self.vehicle_box_dims),actor.get_transform().rotation, 3, self.ghost_color,self.freq)

    def colorVictims(self,coloring_brush,synchronization,victimes):
        victimes_carla_ids = [synchronization.sumo2carla_ids.get(actor_id) for actor_id in victimes]
        for actor_id in victimes_carla_ids:
            if actor_id:
                actor=synchronization.carla.world.get_actor(actor_id)
                coloring_brush.draw_box(carla.BoundingBox(actor.get_transform().location,self.vehicle_box_dims),actor.get_transform().rotation, 3, self.victim_color,self.freq)

    def colorDetections(self,coloring_brush,synchronization,detections):
        for actor_id in detections:
            if synchronization.sumo2carla_ids.get(actor_id):
                actor=synchronization.carla.world.get_actor(synchronization.sumo2carla_ids.get(actor_id))
                coloring_brush.draw_box(carla.BoundingBox(actor.get_transform().location+carla.Vector3D(0,0,5),self.detection_box_dims),actor.get_transform().rotation, 3, self.detection_color,self.freq)
            else :
                ghost_carla_id =list(synchronization.carla2sumo_ids.keys())[list(synchronization.carla2sumo_ids.values()).index(actor_id)]
                actor=synchronization.carla.world.get_actor(ghost_carla_id)
                coloring_brush.draw_box(carla.BoundingBox(actor.get_transform().location+carla.Vector3D(0,0,5),self.detection_box_dims),actor.get_transform().rotation, 3, self.detection_color,self.freq)

    def colorDENMS(self,synchronization,denm):
        coloring_brush = synchronization.carla.world.debug
        direction = math.radians(denm.get("Heading")/10.)
        rel_dist = denm.get('Relevance Distance')
        dist = 0
        if rel_dist == 0:
            dist = 50
        elif rel_dist == 1:
            dist = 100
        elif rel_dist == 2:
            dist = 200
        elif rel_dist == 3:
            dist = 500
        elif rel_dist == 4:
            dist = 1000
        elif rel_dist == 5:
            dist = 5000
        else:
            dist = 10000
        print("Did it!")
        cause = denm.get('Cause Code')
        if cause == 6:
            # Traction Loss
            coloring_brush.draw_box(carla.BoundingBox(carla.Location(denm.get('sender_pos_x'),denm.get('sender_pos_y'),10), carla.Vector3D(dist/2, dist/2, 10)),carla.Rotation(0,0,0),3,color=carla.Color(0,0,255),life_time=denm.get("Validity Duration"))
            coloring_brush.draw_point(carla.Location(denm.get('sender_pos_x'),denm.get('sender_pos_y'),10), size=.1, life_time=denm.get("Validity Duration"))
        elif cause == 99:
            # Emergency Braking
            coloring_brush.draw_box(carla.BoundingBox(carla.Location(denm.get('sender_pos_x'),denm.get('sender_pos_y'),70), carla.Vector3D(dist/2, dist/2, 10)),carla.Rotation(0,0,0),3,color=carla.Color(255,0,0),life_time=denm.get("Validity Duration"))
            coloring_brush.draw_point(carla.Location(denm.get('sender_pos_x'),denm.get('sender_pos_y'),25), size=.1, life_time=denm.get("Validity Duration"))
        elif cause == 1 or cause == 27:
            # Traffic Box
            coloring_brush.draw_box(carla.BoundingBox(carla.Location(denm.get('sender_pos_x'),denm.get('sender_pos_y'),35), carla.Vector3D(dist/2, dist/2, 10)),carla.Rotation(0,0,0),3,color=carla.Color(0,255,0),life_time=denm.get("Validity Duration"))
            coloring_brush.draw_point(carla.Location(denm.get('sender_pos_x'),denm.get('sender_pos_y'),25), life_time=denm.get("Validity Duration"))
        
