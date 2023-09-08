from OpenGL.GL import *

from utils.singleton.Singleton import Singleton
from renderer.model.Model import Model
from renderer.shader.Shader import Shader
from renderer.camera.Camera import Camera

class RendererManager(metaclass=Singleton):
    def __init__(self):
        self.models = dict()

        self.models["plane"] = Model([-0.5, -0.5, 0.0,
                                       0.5, -0.5, 0.0,
                                      -0.5,  0.5, 0.0,
                                       0.5,  0.5, 0.0,
                                      -0.5,  0.5, 0.0,
                                       0.5, -0.5, 0.0])
        
        self.models["plane"].scale(100, 120, 120)
        self.models["plane"].place(0.0, 0.0, 0.0)
        self.models["plane"].rotate(60.0, 30.0, 45.0)

        self.models["box"] = Model("models/gally.obj")
        self.models["box"].scale(100, 100, 100)
        self.models["box"].rotate(0.0, 0.0, 45.0)
        self.models["box"].place(500.0, 0.0, 0.0)

        # self.models["plane"].place(0, 0.5, 0)
        # self.models["plane"].scale(1.1, 0.9, 1.2)
        # self.models["plane"].rotate(45.0, 45.0, 45.0)
        
        self.shaders = dict()
        self.shaders["default"] = Shader("./shaders/default/default.vert", "./shaders/default/default.frag")

        self.camera = Camera()