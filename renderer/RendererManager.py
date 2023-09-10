from OpenGL.GL import *
import numpy as np
import pywavefront
import glm

from utils.Singleton import Singleton
from renderer.model.Mesh import Model
from renderer.shader.Shader import Shader
from renderer.camera.Camera import Camera

class RendererManager(metaclass=Singleton):
    def __init__(self):
        self.meshes = dict()

        self.vertex_vbos = dict()
        self.normal_vbos = dict()
        self.uv_vbos = dict()
        self.vaos = dict()

        self.model_matrices = dict()
        self.vertices_count = dict()
        self.positions = dict()
        self.rotations = dict()
        self.scales = dict()
        self.shaders = dict()

        self.shaders["default"] = Shader("./shaders/default/default.vert", "./shaders/default/default.frag")
        self.shaders["white"] = Shader("./shaders/white/white.vert", "./shaders/white/white.frag")
        self.camera = Camera()

        self.light_source = glm.vec3(10, 10, 10)

    def new_mesh(self, name, vertices, count = 1):
        formatted_vertices = []
        formatted_normals = []
        formatted_uvs = []

        scene = pywavefront.Wavefront(vertices, collect_faces = True)
        for key, material in scene.materials.items():
            for i in range(0, len(material.vertices), 8):
                formatted_uvs.append(material.vertices[i])
                formatted_uvs.append(material.vertices[i+1])

                formatted_normals.append(material.vertices[i+2])
                formatted_normals.append(material.vertices[i+3])
                formatted_normals.append(material.vertices[i+4])

                formatted_vertices.append(material.vertices[i+5])
                formatted_vertices.append(material.vertices[i+6])                
                formatted_vertices.append(material.vertices[i+7])

        formatted_vertices = np.array(formatted_vertices, dtype=np.float32)
        formatted_normals = np.array(formatted_normals, dtype=np.float32)
        formatted_uvs = np.array(formatted_uvs, dtype=np.float32)

        original_name = name

        for i in range(count):
            if count != 1:
                name = original_name + str(i)

            self.vertex_vbos[name] = glGenBuffers(1)
            self.normal_vbos[name] = glGenBuffers(1)
            self.uv_vbos[name] = glGenBuffers(1)

            self.vaos[name] = glGenVertexArrays(1)

            self.vertices_count[name] = len(formatted_vertices) / 3

            glBindVertexArray(self.vaos[name])

            glBindBuffer(GL_ARRAY_BUFFER, self.vertex_vbos[name])
            glBufferData(GL_ARRAY_BUFFER, formatted_vertices.nbytes, formatted_vertices, GL_STATIC_DRAW)
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

            glBindBuffer(GL_ARRAY_BUFFER, self.normal_vbos[name])
            glBufferData(GL_ARRAY_BUFFER, formatted_normals.nbytes, formatted_normals, GL_STATIC_DRAW)
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

            glBindBuffer(GL_ARRAY_BUFFER, self.uv_vbos[name])
            glBufferData(GL_ARRAY_BUFFER, formatted_uvs.nbytes, formatted_uvs, GL_STATIC_DRAW)
            glEnableVertexAttribArray(2)
            glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))     

            self.positions[name] = glm.vec3(0.0)
            self.rotations[name] = glm.vec3(0.0)
            self.scales[name] = glm.vec3(1.0)
            self.model_matrices[name] = glm.mat4(1.0)

    def move(self, name, x, y, z):
        self.positions[name] = glm.vec3(x, y, z)
        self._calculate_model_matrix(name)
    
    def rotate(self, name, x, y, z):
        self.rotations[name] = glm.vec3(x, y, z)
        self._calculate_model_matrix(name)

    def scale(self, name, x, y, z):
        self.scales[name] = glm.vec3(x, y, z)
        self._calculate_model_matrix(name)

    def _calculate_model_matrix(self, name):
        self.model_matrices[name] = glm.mat4(1)
        self.model_matrices[name] = glm.translate(self.model_matrices[name], self.positions[name])
        self.model_matrices[name] = glm.rotate(self.model_matrices[name], glm.radians(self.rotations[name].x), glm.vec3(1.0, 0.0, 0.0))
        self.model_matrices[name] = glm.rotate(self.model_matrices[name], glm.radians(self.rotations[name].y), glm.vec3(0.0, 1.0, 0.0))
        self.model_matrices[name] = glm.rotate(self.model_matrices[name], glm.radians(self.rotations[name].z), glm.vec3(0.0, 0.0, 1.0))
        self.model_matrices[name] = glm.scale(self.model_matrices[name], self.scales[name])

    def get_ogl_matrix(self, name):
        return(glm.value_ptr(self.model_matrices[name]))

##### KEEP IMPLEMENTING DATA ORIENTED PROGRAMMING