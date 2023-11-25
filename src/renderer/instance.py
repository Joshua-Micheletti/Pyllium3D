from OpenGL.GL import *
import numpy as np

from utils.colors import colors

# class to implement an instance for rendering
class Instance:
    # constructor method
    def __init__(self, mesh = "", shader = ""):
        # mesh name for the models in the instance
        self.mesh = mesh
        # shader models in the instance
        self.shader = shader

        # list of models in the instance
        self.models = []

        # array of model matrices of the models in the instance
        self.model_matrices = []
        # array of material components
        self.ambients = []
        self.diffuses = []
        self.speculars = []
        self.shininesses = []
        self.roughnesses = []
        self.metallicnesses = []

        # vbos to store instance specific information (model matrices and materials)
        self.model_matrices_vbo = None
        self.ambient_vbo = None
        self.diffuse_vbo = None
        self.specular_vbo = None
        self.shininess_vbo = None
        self.roughness_vbo = None
        self.metallic_vbo = None

        # vao to interpret the instance informations
        self.vao = None

        self.vertex_vbo = None
        self.normal_vbo = None
        self.uv_vbo = None

        # dictionary to keep track of what to update in the instance every cycle
        self.to_update = dict()

        self.to_update["model_matrices"] = False
        self.to_update["ambients"] = False
        self.to_update["diffuses"] = False
        self.to_update["speculars"] = False
        self.to_update["shininesses"] = False
        self.to_update["roughnesses"] = False
        self.to_update["metallicnesses"] = False

        self.models_to_render = []

    # method to set the mesh in the instance
    def set_mesh(self, mesh, vertex_vbo, normal_vbo, uv_vbo):
        # keep track of the new mesh in the instance
        self.mesh = mesh
        self.vertex_vbo = vertex_vbo
        self.normal_vbo = normal_vbo
        self.uv_vbo = uv_vbo

        # set the buffers in the instance VAO for the mesh

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



    # method to change the model matrix of a model in the instance
    def change_model_matrix(self, model, model_matrix):
        # get the index of the model selected
        model_index = self.models.index(model)

        offset = 0
        # scroll through the columns in the matrix
        for col in model_matrix:
            # scroll through the values in the column
            for value in col:
                # update stored model matrix with the new value
                self.model_matrices[model_index * 16 + offset] = value
                # increase the offset
                offset += 1

    # method to change the ambient value in an instance
    def change_ambient(self, material):
        # get the list of models in this instance that use the changed material
        models_changed = list(set(material.models).intersection(self.models))

        # for every model with that material
        for model in models_changed:
            # get the index of the current model
            model_index = self.models.index(model)
            # change the values of the ambients according to the new material change
            self.ambients[model_index * 3 + 0] = material.ambient[0]
            self.ambients[model_index * 3 + 1] = material.ambient[1]
            self.ambients[model_index * 3 + 2] = material.ambient[2]

    # method to change the diffuse value in an instance
    def change_diffuse(self, material):
        # get the list of models in this instance that use the changed material
        models_changed = list(set(material.models).intersection(self.models))

        # for every model with that material
        for model in models_changed:
            # get the index of the current model
            model_index = self.models.index(model)
            # change the values of the diffuses according to the new material change
            self.diffuses[model_index * 3 + 0] = material.diffuse[0]
            self.diffuses[model_index * 3 + 1] = material.diffuse[1]
            self.diffuses[model_index * 3 + 2] = material.diffuse[2]

    # method to change the specular value in an instance
    def change_specular(self, material):
        # get the list of models in this instance that use the changed material
        models_changed = list(set(material.models).intersection(self.models))

        # for every model with that material
        for model in models_changed:
            # get the index of the current model
            model_index = self.models.index(model)
            # change the values of the specular according to the new material change
            self.speculars[model_index * 3 + 0] = material.specular[0]
            self.speculars[model_index * 3 + 1] = material.specular[1]
            self.speculars[model_index * 3 + 2] = material.specular[2]

    # method to change the shininess value in an instance
    def change_shininess(self, material):
        # get the list of models in this instance that use the changed material
        models_changed = list(set(material.models).intersection(self.models))

        # for every model with that material
        for model in models_changed:
            # get the index of the current model
            model_index = self.models.index(model)
            # change the values of the shininess according to the new material change
            self.shininesses[model_index] = material.shininess

    def change_roughness(self, material):
        # get the list of models in this instance that use the changed material
        models_changed = list(set(material.models).intersection(self.models))

        # for every model with that material
        for model in models_changed:
            # get the index of the current model
            model_index = self.models.index(model)
            # change the values of the shininess according to the new material change
            self.roughnesses[model_index] = material.roughness

    def change_metallic(self, material):
        # get the list of models in this instance that use the changed material
        models_changed = list(set(material.models).intersection(self.models))

        # for every model with that material
        for model in models_changed:
            # get the index of the current model
            model_index = self.models.index(model)
            # change the values of the shininess according to the new material change
            self.metallicnesses[model_index] = material.metallic

    # method to update the properties of the instance
    def update(self):
        # check for each property and update it accordingly
        # if self.to_update["model_matrices"]:
        #     self.update_model_matrices()
        #     self.to_update["model_matrices"] = False
        # if self.to_update["ambients"]:
        #     self.update_ambients()
        #     self.to_update["ambients"] = False
        # if self.to_update["diffuses"]:
        #     self.update_diffuses()
        #     self.to_update["diffuses"] = False
        # if self.to_update["speculars"]:
        #     self.update_speculars()
        #     self.to_update["speculars"] = False
        # if self.to_update["shininesses"]:
        #     self.update_shininesses()
        #     self.to_update["shininesses"] = False
        # if self.to_update["roughnesses"]:
        #     self.update_roughnesses()
        #     self.to_update["roughnesses"] = False
        # if self.to_update["metallicnesses"]:
        #     self.update_metallicnesses()
        #     self.to_update["metallicnesses"] = False
        self.setup_buffers()
        
    # method to update the model matrices vbo
    def update_model_matrices(self):
        # convert the array into a numpy array of float 32bit
        self.model_matrices = np.array(self.model_matrices, dtype=np.float32)
        # bind the model matrices vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.model_matrices_vbo)
        # pass the new data for the vbo
        glBufferSubData(GL_ARRAY_BUFFER, 0, self.model_matrices.nbytes, self.model_matrices)
        # glBufferSubData(GL_ARRAY_BUFFER, 0, self.model_matrices.nbytes, self.model_matrices)
        # bind back to the default vbo
        # glBindBuffer(GL_ARRAY_BUFFER, 0)

    # method to update the ambients vbo
    def update_ambients(self):
        # convert the array into a numpy array of float 32bit
        self.ambients = np.array(self.ambients, dtype=np.float32)
        # bind the ambient vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.ambient_vbo)
        # pass the new data for the vbo
        glBufferData(GL_ARRAY_BUFFER, self.ambients.nbytes, self.ambients, GL_STATIC_DRAW)
        # bind back to the default vbo
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    # method to update the ambients vbo
    def update_diffuses(self):
        # convert the array into a numpy array of float 32bit
        self.diffuses = np.array(self.diffuses, dtype=np.float32)
        # bind the diffuse vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.diffuse_vbo)
        # pass the new data for the vbo
        glBufferData(GL_ARRAY_BUFFER, self.diffuses.nbytes, self.diffuses, GL_STATIC_DRAW)
        # bind back to the default vbo
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    # method to update the ambients vbo
    def update_speculars(self):
        # convert the array into a numpy array of float 32bit
        self.speculars = np.array(self.speculars, dtype=np.float32)
        # bind the specular vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.specular_vbo)
        # pass the new data for the vbo
        glBufferData(GL_ARRAY_BUFFER, self.speculars.nbytes, self.speculars, GL_STATIC_DRAW)
        # bind back to the default vbo
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    # method to update the ambients vbo
    def update_shininesses(self):
        # convert the array into a numpy array of float 32bit
        self.shininesses = np.array(self.shininesses, dtype=np.float32)
        # bind the shininess vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.shininess_vbo)
        # pass the new data for the vbo
        glBufferData(GL_ARRAY_BUFFER, self.shininesses.nbytes, self.shininesses, GL_STATIC_DRAW)
        # bind back to the default vbo
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    # method to update the ambients vbo
    def update_roughnesses(self):
        # convert the array into a numpy array of float 32bit
        self.roughnesses = np.array(self.roughnesses, dtype=np.float32)
        # bind the shininess vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.roughness_vbo)
        # pass the new data for the vbo
        glBufferData(GL_ARRAY_BUFFER, self.roughnesses.nbytes, self.roughnesses, GL_STATIC_DRAW)
        # bind back to the default vbo
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        # print("updated roughnesses")

    # method to update the ambients vbo
    def update_metallicnesses(self):
        # convert the array into a numpy array of float 32bit
        self.metallicnesses = np.array(self.metallicnesses, dtype=np.float32)
        # bind the shininess vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.metallic_vbo)
        # pass the new data for the vbo
        glBufferData(GL_ARRAY_BUFFER, self.metallicnesses.nbytes, self.metallicnesses, GL_STATIC_DRAW)
        # bind back to the default vbo
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        # print("updated metallicnesses")

    def setup_buffers(self):
        if len(self.models_to_render) == 0:
            return()

        render_model_matrices = []
        render_ambients = []
        render_diffuses = []
        render_speculars = []
        render_shininesses = []
        render_roughnesses = []
        render_metallicnesses = []

        for model in self.models_to_render:
            model_index = self.models.index(model)
            # scroll through the columns in the matrix
            for i in range(16):
                # update stored model matrix with the new value
                render_model_matrices.append(self.model_matrices[model_index * 16 + i])

            for i in range(3):
                render_ambients.append(self.ambients[model_index * 3 + i])
            
            for i in range(3):
                render_diffuses.append(self.diffuses[model_index * 3 + i])

            for i in range(3):
                render_speculars.append(self.speculars[model_index * 3 + i])

            render_shininesses.append(self.shininesses[model_index])
            render_roughnesses.append(self.roughnesses[model_index])
            render_metallicnesses.append(self.metallicnesses[model_index])

        render_model_matrices = np.array(render_model_matrices, dtype=np.float32)
        render_ambients = np.array(render_ambients, dtype=np.float32)
        render_diffuses = np.array(render_diffuses, dtype=np.float32)
        render_speculars = np.array(render_speculars, dtype=np.float32)
        render_shininesses = np.array(render_shininesses, dtype=np.float32)
        render_roughnesses = np.array(render_roughnesses, dtype=np.float32)
        render_metallicnesses = np.array(render_metallicnesses, dtype=np.float32)

        # bind the ambient vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.model_matrices_vbo)
        # pass the new data for the vbo
        glBufferData(GL_ARRAY_BUFFER, render_model_matrices.nbytes, render_model_matrices, GL_STATIC_DRAW)
        # bind back to the default vbo
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        # bind the ambient vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.ambient_vbo)
        # pass the new data for the vbo
        glBufferData(GL_ARRAY_BUFFER, render_ambients.nbytes, render_ambients, GL_STATIC_DRAW)
        # bind back to the default vbo
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        # bind the ambient vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.diffuse_vbo)
        # pass the new data for the vbo
        glBufferData(GL_ARRAY_BUFFER, render_diffuses.nbytes, render_diffuses, GL_STATIC_DRAW)
        # bind back to the default vbo
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        # bind the ambient vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.specular_vbo)
        # pass the new data for the vbo
        glBufferData(GL_ARRAY_BUFFER, render_speculars.nbytes, render_speculars, GL_STATIC_DRAW)
        # bind back to the default vbo
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        # bind the ambient vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.shininess_vbo)
        # pass the new data for the vbo
        glBufferData(GL_ARRAY_BUFFER, render_shininesses.nbytes, render_shininesses, GL_STATIC_DRAW)
        # bind back to the default vbo
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        # bind the ambient vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.roughness_vbo)
        # pass the new data for the vbo
        glBufferData(GL_ARRAY_BUFFER, render_roughnesses.nbytes, render_roughnesses, GL_STATIC_DRAW)
        # bind back to the default vbo
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        # bind the ambient vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.metallic_vbo)
        # pass the new data for the vbo
        glBufferData(GL_ARRAY_BUFFER, render_metallicnesses.nbytes, render_metallicnesses, GL_STATIC_DRAW)
        # bind back to the default vbo
        glBindBuffer(GL_ARRAY_BUFFER, 0)