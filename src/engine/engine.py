from physics.physics_world import PhysicsWorld
from renderer.renderer_manager.renderer_manager import RendererManager
from utils import Singleton


class Engine(metaclass=Singleton):
    def __init__(self):
        self.links = {}

    def create_link(self, physics_body, model):
        self.links[physics_body] = model

    def update(self):
        rm = RendererManager()
        pw = PhysicsWorld()

        for physics_body, model in self.links.items():
            position, rotation = pw.get_position_rotation(physics_body)
            rm.place(model, *position)
            rm.rotate(model, *rotation)
