from OpenGL.GL import *
import numpy as np

# from renderer.RendererManager import RendererManager
from utils.colors import colors

class Instance:

    def __init__(self, mesh = "", shader = ""):
        self.mesh = mesh
        self.shader = shader

        self.models = []
        # self.model_matrices = dict()
        # self.ambients = dict()
        # self.diffuses = dict()
        # self.speculars = dict()
        # self.shininesses = dict()

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

        # self.formatted_matrices = []
        # self.formatted_ambients = []
        # self.formatted_diffuses = []
        # self.formatted_speculars = []
        # self.formatted_shininesses = []

        self.changed_ambients = []
        self.changed_diffuses = []
        self.changed_speculars = []
        self.changed_shininesses = []

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




    def update(self, model_matrices, materials):
        if self.to_update["model_matrices"]:
            self.update_model_matrices(model_matrices)
            self.to_update["model_matrices"] = False

        if self.to_update["ambients"]:
            self.update_ambients(materials)
            self.to_update["ambients"] = False
        if self.to_update["diffuses"]:
            self.update_diffuses(materials)
            self.to_update["diffuses"] = False
        if self.to_update["speculars"]:
            self.update_speculars(materials)
            self.to_update["speculars"] = False
        if self.to_update["shininesses"]:
            self.update_shininesses(materials)
            self.to_update["shininesses"] = False
        

    def update_model_matrices(self, model_matrices):
        formatted_model_matrices = []

        for model in self.models:
            for col in model_matrices[model.name]:
                for value in col:
                    formatted_model_matrices.append(value)

        # convert the list into an array of 32bit floats
        formatted_model_matrices = np.array(formatted_model_matrices, dtype=np.float32)
        # get the size in bits of an item in the matrices list
        float_size = formatted_model_matrices.itemsize
    
        # bind the new buffer
        glBindBuffer(GL_ARRAY_BUFFER, self.model_matrices_vbo)
        # pass the data to the buffer
        glBufferData(GL_ARRAY_BUFFER, float_size * len(formatted_model_matrices), formatted_model_matrices, GL_STATIC_DRAW)
        
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def update_ambients(self, materials):
        # formatted_ambients = []
        
        # for model in self.models:
        #     formatted_ambients.append(materials[model.material]["ambient"].x)
        #     formatted_ambients.append(materials[model.material]["ambient"].y)
        #     formatted_ambients.append(materials[model.material]["ambient"].z)
        
        # formatted_ambients = np.array(formatted_ambients, dtype=np.float32)

        float_size = formatted_ambients.itemsize

        glBindBuffer(GL_ARRAY_BUFFER, self.ambient_vbo)
        glBufferData(GL_ARRAY_BUFFER, float_size * len(formatted_ambients), formatted_ambients, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def update_diffuses(self, materials):
        formatted_diffuses = []
        
        for model in self.models:
            formatted_diffuses.append(materials[model.material]["diffuse"].x)
            formatted_diffuses.append(materials[model.material]["diffuse"].y)
            formatted_diffuses.append(materials[model.material]["diffuse"].z)
        
        formatted_diffuses = np.array(formatted_diffuses, dtype=np.float32)

        float_size = formatted_diffuses.itemsize

        glBindBuffer(GL_ARRAY_BUFFER, self.diffuse_vbo)
        glBufferData(GL_ARRAY_BUFFER, float_size * len(formatted_diffuses), formatted_diffuses, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def update_speculars(self, materials):
        formatted_speculars = []
        
        for model in self.models:
            formatted_speculars.append(materials[model.material]["specular"].x)
            formatted_speculars.append(materials[model.material]["specular"].y)
            formatted_speculars.append(materials[model.material]["specular"].z)
        
        formatted_speculars = np.array(formatted_speculars, dtype=np.float32)

        float_size = formatted_speculars.itemsize

        glBindBuffer(GL_ARRAY_BUFFER, self.specular_vbo)
        glBufferData(GL_ARRAY_BUFFER, float_size * len(formatted_speculars), formatted_speculars, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def update_shininesses(self, materials):
        formatted_shininesses = []
        
        for model in self.models:
            formatted_shininesses.append(materials[model.material]["shininess"])
        
        formatted_shininesses = np.array(formatted_shininesses, dtype=np.float32)

        float_size = formatted_shininesses.itemsize

        glBindBuffer(GL_ARRAY_BUFFER, self.shininess_vbo)
        glBufferData(GL_ARRAY_BUFFER, float_size * len(formatted_shininesses), formatted_shininesses, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
