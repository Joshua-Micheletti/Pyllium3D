import pybullet as pb
import glm

from utils.singleton import Singleton
from utils.messages import *

class PhysicsWorld(metaclass=Singleton):
    def __init__(self):
        self.physics_client = pb.connect(pb.DIRECT)
        
        self.shapes = dict()
        self.rigid_bodies = dict()

        pb.setGravity(0.0, -9.8, 0)

        pb.setTimeStep(1/60)

        self._setup_scene()

        print_success("initialized physics world")

    def _setup_scene(self):
        self.shapes["sphere"] = pb.createCollisionShape(pb.GEOM_SPHERE, radius=0.5)
        self.shapes["plane"] = pb.createCollisionShape(pb.GEOM_PLANE, planeNormal=[0, 1, 0])

        self.rigid_bodies["sphere"] = pb.createMultiBody(baseMass=1.0, baseCollisionShapeIndex=self.shapes["sphere"])
        self.rigid_bodies["plane"] = pb.createMultiBody(baseMass=0.0, baseCollisionShapeIndex=self.shapes["plane"])

    def create_sphere_shape(self, name, radius=0.5):
        self.shapes[name] = pb.createCollisionShape(pb.GEOM_SPHERE, radius=radius)

    def create_plane_shape(self, name, planeNormal=[0, 1, 0]):
        self.shapes[name] = pb.createCollisionShape(pb.GEOM_PLANE, planeNormal=planeNormal)

    def create_box_shape(self, name, dimensions=[0.25, 0.25, 0.25]):
        self.shapes[name] = pb.createCollisionShape(pb.GEOM_BOX, halfExtents=dimensions)

    def new_body(self, name, shape="sphere", mass=1, position=[0, 0, 0], orientation=[1.0, 0.0, 0.0, 0.0]):
        self.rigid_bodies[name] = pb.createMultiBody(baseMass=mass, baseCollisionShapeIndex=self.shapes[shape], basePosition=position, baseOrientation=orientation)

    def update(self):
        pb.stepSimulation(self.physics_client)

    def get_position_rotation(self, physics_body):
        position, rotation = pb.getBasePositionAndOrientation(self.rigid_bodies[physics_body])

        euler_rotation = pb.getEulerFromQuaternion(rotation)

        degree_euler_rotation = (glm.degrees(euler_rotation[0]), glm.degrees(euler_rotation[1]), glm.degrees(euler_rotation[2]))
        # euler_rotation[0] = glm.degrees(euler_rotation[0])
        # euler_rotation[1] = glm.degrees(euler_rotation[1])
        # euler_rotation[2] = glm.degrees(euler_rotation[2])

        return(position, degree_euler_rotation)
        # return(pb.getBasePositionAndOrientation(self.rigid_bodies[physics_body]))
