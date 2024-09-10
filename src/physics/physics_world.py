import glm
import pybullet as pb

from utils import Singleton, print_success


class PhysicsWorld(metaclass=Singleton):
    def __init__(self):
        self.physics_client = pb.connect(pb.DIRECT)

        self.shapes = dict()
        self.rigid_bodies = dict()

        pb.setGravity(0.0, -20, 0)

        pb.setTimeStep(1 / 60)

        self._setup_scene()

        print_success('initialized physics world')

    def _setup_scene(self):
        self.shapes['sphere'] = pb.createCollisionShape(pb.GEOM_SPHERE, radius=1)
        self.shapes['plane'] = pb.createCollisionShape(pb.GEOM_PLANE, planeNormal=[0, 0, 1])
        self.shapes['box'] = pb.createCollisionShape(pb.GEOM_BOX, halfExtents=[1, 1, 1])

        # self.rigid_bodies["sphere"] = pb.createMultiBody(baseMass=1.0, baseCollisionShapeIndex=self.shapes["sphere"])
        # self.rigid_bodies["plane"] = pb.createMultiBody(baseMass=0.0, baseCollisionShapeIndex=self.shapes["plane"])

    def create_sphere_shape(self, name, radius=0.5):
        self.shapes[name] = pb.createCollisionShape(pb.GEOM_SPHERE, radius=radius)

    def create_plane_shape(self, name, planeNormal=[0, 1, 0]):
        self.shapes[name] = pb.createCollisionShape(pb.GEOM_PLANE, planeNormal=planeNormal)

    def create_box_shape(self, name, dimensions=[0.25, 0.25, 0.25]):
        self.shapes[name] = pb.createCollisionShape(pb.GEOM_BOX, halfExtents=dimensions)

    def new_body(
        self,
        name,
        shape='sphere',
        mass=1,
        position=[0, 0, 0],
        orientation=[1.0, 0.0, 0.0, 0.0],
    ):
        if mass == None:
            mass = 1
        if position == None:
            position = [0, 0, 0]
        if orientation == None:
            orientation = [1.0, 0.0, 0.0, 0.0]

        self.rigid_bodies[name] = pb.createMultiBody(
            baseMass=mass,
            baseCollisionShapeIndex=self.shapes[shape],
            basePosition=position,
            baseOrientation=orientation,
        )

    def update(self):
        pb.stepSimulation(self.physics_client)

    def get_position_rotation(self, physics_body):
        position, rotation = pb.getBasePositionAndOrientation(self.rigid_bodies[physics_body])

        euler_rotation = pb.getEulerFromQuaternion(rotation)

        degree_euler_rotation = (
            glm.degrees(euler_rotation[0]),
            glm.degrees(euler_rotation[1]),
            glm.degrees(euler_rotation[2]),
        )
        # euler_rotation[0] = glm.degrees(euler_rotation[0])
        # euler_rotation[1] = glm.degrees(euler_rotation[1])
        # euler_rotation[2] = glm.degrees(euler_rotation[2])

        return (position, degree_euler_rotation)
        # return(pb.getBasePositionAndOrientation(self.rigid_bodies[physics_body]))

    def place(self, physics_body: str, x: float, y: float, z: float) -> None:
        position, rotation = pb.getBasePositionAndOrientation(self.rigid_bodies[physics_body])

        pb.resetBasePositionAndOrientation(self.rigid_bodies.get(physics_body), [x, y, z], rotation)

    def move(self, physics_body: str, x: float, y: float, z: float) -> None:
        position, rotation = pb.getBasePositionAndOrientation(self.rigid_bodies[physics_body])
        pb.resetBasePositionAndOrientation(
            self.rigid_bodies.get(physics_body),
            [x + position[0], y + position[1], z + position[2]],
            rotation,
        )
