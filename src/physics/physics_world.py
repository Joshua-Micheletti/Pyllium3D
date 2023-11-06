import pybullet as pb

from utils.singleton import Singleton
from utils.messages import *

class PhysicsWorld(metaclass=Singleton):
    def __init__(self):
        self.physics_client = pb.connect(pb.DIRECT)
        
        self.shapes = dict()
        self.rigid_bodies = dict()

        pb.setGravity(0.0, -9.8, 0)

        self._setup_scene()

        print_success("initialized physics world")

    def _setup_scene(self):
        self.shapes["sphere"] = pb.createCollisionShape(pb.GEOM_SPHERE, radius=0.5)
        self.shapes["plane"] = pb.createCollisionShape(pb.GEOM_PLANE, planeNormal=[0, 1, 0])

        self.rigid_bodies["sphere"] = pb.createMultiBody(baseMass=1.0, baseCollisionShapeIndex=self.shapes["sphere"])
        self.rigid_bodies["plane"] = pb.createMultiBody(baseMass=0.0, baseCollisionShapeIndex=self.shapes["plane"])

    def create_shape(self, name, type, radius=0.5, planeNormal=[0, 1, 0]):
        if type == "plane":
            self.shapes[name] = pb.createCollisionShape(pb.GEOM_PLANE, planeNormal=planeNormal)
        elif type == "sphere":
            self.shapes[name] = pb.createCollisionShape(pb.GEOM_SPHERE, radius=radius)

    def create_body(self, name, shape, mass, position):
        self.rigid_bodies[name] = pb.createMultiBody(baseMass=mass, baseCollisionShapeIndex=self.shapes[shape], basePosition=position)

    def update(self):
        pb.stepSimulation(self.physics_client)

    def get_position_rotation(self, physics_body):
        return(pb.getBasePositionAndOrientation(self.rigid_bodies[physics_body]))
