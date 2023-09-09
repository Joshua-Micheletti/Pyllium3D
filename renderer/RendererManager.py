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
        self.vbos = dict()
        self.vaos = dict()
        self.model_matrices = dict()
        self.vertices_count = dict()
        self.positions = dict()
        self.rotations = dict()
        self.scales = dict()
        self.shaders = dict()

        self.shaders["default"] = Shader("./shaders/default/default.vert", "./shaders/default/default.frag")
        self.camera = Camera()

    def new_mesh(self, name, vertices):
        self.vbos[name] = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbos[name])

        self.vaos[name] = glGenVertexArrays(1)
        glBindVertexArray(self.vaos[name])
        

        self.vertices_count[name] = 0

        formatted_vertices = []

        if not isinstance(vertices, str):
            formatted_vertices = np.array(vertices, dtype=np.float32)
            self.vertices_count[name] = len(vertices) / 3

        else:
            scene = pywavefront.Wavefront(vertices, collect_faces = True)
            for mesh in scene.mesh_list:                
                for face in mesh.faces:
                    formatted_vertices.append(scene.vertices[face[0]][0])
                    formatted_vertices.append(scene.vertices[face[0]][1])
                    formatted_vertices.append(scene.vertices[face[0]][2])

                    formatted_vertices.append(scene.vertices[face[1]][0])
                    formatted_vertices.append(scene.vertices[face[1]][1])
                    formatted_vertices.append(scene.vertices[face[1]][2])

                    formatted_vertices.append(scene.vertices[face[2]][0])
                    formatted_vertices.append(scene.vertices[face[2]][1])
                    formatted_vertices.append(scene.vertices[face[2]][2])
            
            self.vertices_count[name] = len(formatted_vertices) / 3
            # print(formatted_vertices)

            formatted_vertices = np.array(formatted_vertices, dtype=np.float32)

        glBufferData(GL_ARRAY_BUFFER, formatted_vertices.nbytes, formatted_vertices, GL_STATIC_DRAW) 

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
       


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