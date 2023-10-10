from OpenGL.GL import *
import numpy as np

# from renderer.RendererManager import RendererManager
from utils.colors import colors

class Instance:

    def __init__(self, mesh = "", shader = ""):
        self.mesh = mesh
        self.shader = shader

        self.models = []

        self.model_matrices = []
        self.ambients = []
        self.diffuses = []
        self.speculars = []
        self.shininesses = []

        self.model_matrices_vbo = None
        self.vao = None
        self.ambient_vbo = None
        self.diffuse_vbo = None
        self.specular_vbo = None
        self.shininess_vbo = None

        self.vertex_vbo = None
        self.normal_vbo = None
        self.uv_vbo = None

        self.to_update = dict()

        self.to_update["model_matrices"] = False
        self.to_update["ambients"] = False
        self.to_update["diffuses"] = False
        self.to_update["speculars"] = False
        self.to_update["shininesses"] = False

    def set_mesh(self, mesh, vertex_vbo, normal_vbo, uv_vbo):
        self.mesh = mesh
        self.vertex_vbo = vertex_vbo
        self.normal_vbo = normal_vbo
        self.uv_vbo = uv_vbo

        # bind the vertex vbo of the mesh of the instance
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_vbo)
        # enable the index 0 of the VAO
        glEnableVertexAttribArray(0)
        # link the VBO to the index 0 of the VAO and interpret it as 3 floats
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        # bind the normals vbo of the mesh of the instance
        glBindBuffer(GL_ARRAY_BUFFER, self.normal_vbo)
        # enable the index 1 of the VAO
        glEnableVertexAttribArray(1)
        # link the VBO to the index 1 of the VAO and interpret it as 3 floats
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        # bind the uv vbo of the mesh of the instance
        glBindBuffer(GL_ARRAY_BUFFER, self.uv_vbo)
        # enable the index 2 of the VAO
        glEnableVertexAttribArray(2)
        # link the VBO to the index 2 of the VAO and interpret it as 2 floats
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

    def change_model_matrix(self, model, model_matrix):
        model_index = self.models.index(model)

        offset = 0

        for col in model_matrix:
            for value in col:
                self.model_matrices[model_index * 16 + offset] = value
                offset += 1


    def change_ambient(self, material):
        models_changed = list(set(material.models).intersection(self.models))

        for model in models_changed:
            # print(model.name)
            model_index = self.models.index(model)

            self.ambients[model_index * 3 + 0] = material.ambient[0]
            self.ambients[model_index * 3 + 1] = material.ambient[1]
            self.ambients[model_index * 3 + 2] = material.ambient[2]

    def change_diffuse(self, material):
        models_changed = list(set(material.models).intersection(self.models))

        for model in models_changed:
            model_index = self.models.index(model)

            self.diffuses[model_index * 3 + 0] = material.diffuse[0]
            self.diffuses[model_index * 3 + 1] = material.diffuse[1]
            self.diffuses[model_index * 3 + 2] = material.diffuse[2]

    def change_specular(self, material):
        models_changed = list(set(material.models).intersection(self.models))

        for model in models_changed:
            model_index = self.models.index(model)

            self.speculars[model_index * 3 + 0] = material.specular[0]
            self.speculars[model_index * 3 + 1] = material.specular[1]
            self.speculars[model_index * 3 + 2] = material.specular[2]

    def change_shininess(self, material):
        models_changed = list(set(material.models).intersection(self.models))

        for model in models_changed:
            model_index = self.models.index(model)

            self.shininesses[model_index] = material.shininess


    def update(self):
        if self.to_update["model_matrices"]:
            self.update_model_matrices()
            self.to_update["model_matrices"] = False

        if self.to_update["ambients"]:
            self.update_ambients()
            self.to_update["ambients"] = False
        if self.to_update["diffuses"]:
            self.update_diffuses()
            self.to_update["diffuses"] = False
        if self.to_update["speculars"]:
            self.update_speculars()
            self.to_update["speculars"] = False
        if self.to_update["shininesses"]:
            self.update_shininesses()
            self.to_update["shininesses"] = False
        

    def update_model_matrices(self):
        self.model_matrices = np.array(self.model_matrices, dtype=np.float32)
        float_size = self.model_matrices.itemsize
        glBindBuffer(GL_ARRAY_BUFFER, self.model_matrices_vbo)
        glBufferData(GL_ARRAY_BUFFER, float_size * len(self.model_matrices), self.model_matrices, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def update_ambients(self):
        self.ambients = np.array(self.ambients, dtype=np.float32)
        float_size = self.ambients.itemsize
        glBindBuffer(GL_ARRAY_BUFFER, self.ambient_vbo)
        glBufferData(GL_ARRAY_BUFFER, float_size * len(self.ambients), self.ambients, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def update_diffuses(self):
        self.diffuses = np.array(self.diffuses, dtype=np.float32)
        float_size = self.diffuses.itemsize
        glBindBuffer(GL_ARRAY_BUFFER, self.diffuse_vbo)
        glBufferData(GL_ARRAY_BUFFER, float_size * len(self.diffuses), self.diffuses, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def update_speculars(self):
        self.speculars = np.array(self.speculars, dtype=np.float32)
        float_size = self.speculars.itemsize
        glBindBuffer(GL_ARRAY_BUFFER, self.specular_vbo)
        glBufferData(GL_ARRAY_BUFFER, float_size * len(self.speculars), self.speculars, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def update_shininesses(self):
        self.shininesses = np.array(self.shininesses, dtype=np.float32)
        float_size = self.shininesses.itemsize
        glBindBuffer(GL_ARRAY_BUFFER, self.shininess_vbo)
        glBufferData(GL_ARRAY_BUFFER, float_size * len(self.shininesses), self.shininesses, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
