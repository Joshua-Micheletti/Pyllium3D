from utils.singleton import Singleton
from renderer.renderer_manager import RendererManager
from physics.physics_world import PhysicsWorld


class Engine(metaclass=Singleton):
    def __init__(self):
        self.links = dict()

    def create_link(self, physics_body, model):
        self.links[physics_body] = model

    def update(self):
        rm = RendererManager()
        pw = PhysicsWorld()

        for physics_body, model in self.links.items():
            position, rotation = pw.get_position_rotation(physics_body)
            rm.place(model, *position)
