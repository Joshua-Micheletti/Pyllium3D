from OpenGL.GL import *
import numpy as np
import glm
import pywavefront

class Model:
    def __init__(self, vertices):
        self.vbo = 0
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vertices_count = 0
        

        formatted_vertices = []

        if not isinstance(vertices, str):
            formatted_vertices = np.array(vertices, dtype=np.float32)
            self.vertices_count = len(vertices) / 3

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
            
            self.vertices_count = len(formatted_vertices) / 3
            # print(formatted_vertices)

            formatted_vertices = np.array(formatted_vertices, dtype=np.float32)

        glBufferData(GL_ARRAY_BUFFER, formatted_vertices.nbytes, formatted_vertices, GL_STATIC_DRAW)        

        self.model_matrix = glm.mat4(1.0)

        self.position = glm.vec3(0.0)
        self.rotation = glm.vec3(0.0)
        self.scale_factor = glm.vec3(1.0)
        self._calculate_model_matrix()

    def place(self, x, y, z):
        self.position = glm.vec3(x, y, z)
        self._calculate_model_matrix()

    def scale(self, x, y, z):
        self.scale_factor = glm.vec3(x, y, z)
        self._calculate_model_matrix()

    def rotate(self, x, y, z):
        self.rotation = glm.vec3(x, y, z)
        self._calculate_model_matrix()

    def _calculate_model_matrix(self):
        self.model_matrix = glm.mat4(1)
        self.model_matrix = glm.translate(self.model_matrix, self.position)
        self.model_matrix = glm.rotate(self.model_matrix, glm.radians(self.rotation.x), glm.vec3(1.0, 0.0, 0.0))
        self.model_matrix = glm.rotate(self.model_matrix, glm.radians(self.rotation.y), glm.vec3(0.0, 1.0, 0.0))
        self.model_matrix = glm.rotate(self.model_matrix, glm.radians(self.rotation.z), glm.vec3(0.0, 0.0, 1.0))
        self.model_matrix = glm.scale(self.model_matrix, self.scale_factor)

    def get_ogl_matrix(self):
        return(glm.value_ptr(self.model_matrix))
        
        

    