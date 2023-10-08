from OpenGL.GL import *
import numpy as np

# from renderer.RendererManager import RendererManager
from utils.colors import colors

class Instance:

    def __init__(self, mesh = "", shader = ""):
        self.models = []
        self.model_matrices = []
        self.model_matrices_vbo = None
        self.vao = None
        self.mesh = mesh
        self.shader = shader

        self.to_update = True