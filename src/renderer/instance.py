import numpy as np
from OpenGL.GL import *


# class to implement an instance for rendering
class Instance:
    # constructor method
    def __init__(self, mesh='', shader=''):
        # mesh name for the models in the instance
        self.mesh = mesh
        # shader models in the instance
        self.shader = shader

        # list of models in the instance
        self.models = dict()

        # array of model matrices of the models in the instance
        self.model_matrices = dict()
        # array of material components
        self.ambients = dict()
        self.diffuses = dict()
        self.speculars = dict()
        self.shininesses = dict()
        self.roughnesses = dict()
        self.metallicnesses = dict()

        self.render_model_matrices = dict()
        self.render_ambients = dict()
        self.render_diffuses = dict()
        self.render_speculars = dict()
        self.render_shininesses = dict()
        self.render_roughnesses = dict()
        self.render_metallicnesses = dict()

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

        self.to_update['model_matrices'] = False
        self.to_update['ambients'] = False
        self.to_update['diffuses'] = False
        self.to_update['speculars'] = False
        self.to_update['shininesses'] = False
        self.to_update['roughnesses'] = False
        self.to_update['metallicnesses'] = False

        self.models_to_render = dict()
        self.previous_models_to_render = dict()
        self.changed_models = set()

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
        # model_index = self.models.index(model)

        # offset = 0
        # # scroll through the columns in the matrix
        # for col in model_matrix:
        #     # scroll through the values in the column
        #     for value in col:
        #         # update stored model matrix with the new value
        #         self.model_matrices[model_index * 16 + offset] = value
        #         # increase the offset
        #         offset += 1
        matrix = []
        for col in model_matrix:
            for value in col:
                matrix.append(value)
        self.model_matrices[model.name] = matrix
        self.changed_models.add(model.name)

    # method to change the ambient value in an instance
    def change_ambient(self, material):
        # get the list of models in this instance that use the changed material
        models_changed = list(set(material.models).intersection(set(self.models.values())))

        # ambient = []
        # for every model with that material
        for model in models_changed:
            # change the values of the ambients according to the new material change
            # ambient.append(material.ambient[0])
            # ambient.append(material.ambient[1])
            # ambient.append(material.ambient[2])
            self.ambients[model.name] = material.ambient
            self.changed_models.add(model.name)

    # method to change the diffuse value in an instance
    def change_diffuse(self, material):
        # get the list of models in this instance that use the changed material
        models_changed = list(set(material.models).intersection(set(self.models.values())))

        # for every model with that material
        for model in models_changed:
            # get the index of the current model
            # model_index = self.models.index(model)
            # change the values of the diffuses according to the new material change
            # self.diffuses[model_index * 3 + 0] = material.diffuse[0]
            # self.diffuses[model_index * 3 + 1] = material.diffuse[1]
            # self.diffuses[model_index * 3 + 2] = material.diffuse[2]
            # diffuse.append(materials.diffuse[0])
            self.diffuses[model.name] = material.diffuse
            self.changed_models.add(model.name)

    # method to change the specular value in an instance
    def change_specular(self, material):
        # get the list of models in this instance that use the changed material
        models_changed = list(set(material.models).intersection(set(self.models.values())))

        # for every model with that material
        for model in models_changed:
            # get the index of the current model
            # model_index = self.models.index(model)
            # # change the values of the specular according to the new material change
            # self.speculars[model_index * 3 + 0] = material.specular[0]
            # self.speculars[model_index * 3 + 1] = material.specular[1]
            # self.speculars[model_index * 3 + 2] = material.specular[2]
            self.speculars[model.name] = material.specular
            self.changed_models.add(model.name)

    # method to change the shininess value in an instance
    def change_shininess(self, material):
        # get the list of models in this instance that use the changed material
        models_changed = list(set(material.models).intersection(set(self.models.values())))

        # for every model with that material
        for model in models_changed:
            # get the index of the current model
            # model_index = self.models.index(model)
            # # change the values of the shininess according to the new material change
            # self.shininesses[model_index] = material.shininess
            self.shininesses[model.name] = material.shininess
            self.changed_models.add(model.name)

    def change_roughness(self, material):
        # get the list of models in this instance that use the changed material
        models_changed = list(set(material.models).intersection(set(self.models.values())))

        # for every model with that material
        for model in models_changed:
            # get the index of the current model
            # model_index = self.models.index(model)
            # # change the values of the shininess according to the new material change
            # self.roughnesses[model_index] = material.roughness
            self.roughnesses[model.name] = material.roughness
            self.changed_models.add(model.name)

    def change_metallic(self, material):
        # get the list of models in this instance that use the changed material
        models_changed = list(set(material.models).intersection(set(self.models.values())))

        # for every model with that material
        for model in models_changed:
            # get the index of the current model
            # model_index = self.models.index(model)
            # # change the values of the shininess according to the new material change
            # self.metallicnesses[model_index] = material.metallic
            self.metallicnesses[model.name] = material.metallic
            self.changed_models.add(model.name)

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
        self.model_matrices = np.array(list(self.model_matrices.values()), dtype=np.float32).flatten()
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
        new_ambients = np.array(list(self.ambients.values()), dtype=np.float32).flatten()
        # bind the ambient vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.ambient_vbo)
        # pass the new data for the vbo
        glBufferData(GL_ARRAY_BUFFER, self.ambients.nbytes, self.ambients, GL_STATIC_DRAW)
        # bind back to the default vbo
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    # method to update the ambients vbo
    def update_diffuses(self):
        # convert the array into a numpy array of float 32bit
        self.diffuses = np.array(list(self.diffuses.values()), dtype=np.float32).flatten()
        # bind the diffuse vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.diffuse_vbo)
        # pass the new data for the vbo
        glBufferData(GL_ARRAY_BUFFER, self.diffuses.nbytes, self.diffuses, GL_STATIC_DRAW)
        # bind back to the default vbo
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    # method to update the ambients vbo
    def update_speculars(self):
        # convert the array into a numpy array of float 32bit
        self.speculars = np.array(list(self.speculars.values()), dtype=np.float32).flatten()
        # bind the specular vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.specular_vbo)
        # pass the new data for the vbo
        glBufferData(GL_ARRAY_BUFFER, self.speculars.nbytes, self.speculars, GL_STATIC_DRAW)
        # bind back to the default vbo
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    # method to update the ambients vbo
    def update_shininesses(self):
        # convert the array into a numpy array of float 32bit
        self.shininesses = np.array(list(self.shininesses.values()), dtype=np.float32)
        # bind the shininess vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.shininess_vbo)
        # pass the new data for the vbo
        glBufferData(GL_ARRAY_BUFFER, self.shininesses.nbytes, self.shininesses, GL_STATIC_DRAW)
        # bind back to the default vbo
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    # method to update the ambients vbo
    def update_roughnesses(self):
        # convert the array into a numpy array of float 32bit
        self.roughnesses = np.array(list(self.roughnesses.values()), dtype=np.float32)
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
        self.metallicnesses = np.array(list(self.metallicnesses.values()), dtype=np.float32)
        # bind the shininess vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.metallic_vbo)
        # pass the new data for the vbo
        glBufferData(GL_ARRAY_BUFFER, self.metallicnesses.nbytes, self.metallicnesses, GL_STATIC_DRAW)
        # bind back to the default vbo
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        # print("updated metallicnesses")

    def setup_buffers(self):
        if len(self.models_to_render) == 0:
            return ()

        if self.models_to_render == self.previous_models_to_render and len(self.changed_models) == 0:
            return ()

        intersection = set(self.previous_models_to_render) & set(self.models_to_render)
        models_to_remove = set(self.previous_models_to_render) - intersection
        models_to_add = (set(self.models_to_render) - intersection).union(self.changed_models)

        models_to_update = intersection & self.changed_models

        models_to_remove = models_to_remove.union(models_to_update)
        models_to_add = models_to_add.union(models_to_update)

        self.changed_models = set()

        for name in models_to_remove:
            self.render_model_matrices.pop(name)
            # self.render_ambients.pop(name)
            self.render_diffuses.pop(name)
            # self.render_speculars.pop(name)
            # self.render_shininesses.pop(name)
            self.render_roughnesses.pop(name)
            self.render_metallicnesses.pop(name)

        for name in models_to_add:
            self.render_model_matrices[name] = self.model_matrices[name]
            # self.render_ambients[name] = self.ambients[name]
            self.render_diffuses[name] = self.diffuses[name]
            # self.render_speculars[name] = self.speculars[name]
            # self.render_shininesses[name] = self.shininesses[name]
            self.render_roughnesses[name] = self.roughnesses[name]
            self.render_metallicnesses[name] = self.metallicnesses[name]

        model_matrices_array = np.array(list(self.render_model_matrices.values()), dtype=np.float32).flatten()
        # bind the ambient vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.model_matrices_vbo)
        # pass the new data for the vbo
        # glBufferData(GL_ARRAY_BUFFER, model_matrices_array.nbytes, model_matrices_array, GL_STREAM_DRAW)
        glBufferSubData(GL_ARRAY_BUFFER, 0, model_matrices_array.nbytes, model_matrices_array)
        # bind back to the default vbo
        # glBindBuffer(GL_ARRAY_BUFFER, 0)

        # ambients_array = np.array(list(self.render_ambients.values()), dtype=np.float32).flatten()
        # # bind the ambient vbo
        # glBindBuffer(GL_ARRAY_BUFFER, self.ambient_vbo)
        # # pass the new data for the vbo
        # glBufferData(GL_ARRAY_BUFFER, ambients_array.nbytes, ambients_array, GL_STATIC_DRAW)
        # # bind back to the default vbo
        # glBindBuffer(GL_ARRAY_BUFFER, 0)

        diffuses_array = np.array(list(self.render_diffuses.values()), dtype=np.float32).flatten()
        # bind the ambient vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.diffuse_vbo)
        # pass the new data for the vbo
        # glBufferData(GL_ARRAY_BUFFER, diffuses_array.nbytes, diffuses_array, GL_STREAM_DRAW)
        glBufferSubData(GL_ARRAY_BUFFER, 0, diffuses_array.nbytes, diffuses_array)
        # bind back to the default vbo
        # glBindBuffer(GL_ARRAY_BUFFER, 0)

        # speculars_array = np.array(list(self.render_speculars.values()), dtype=np.float32).flatten()
        # # bind the ambient vbo
        # glBindBuffer(GL_ARRAY_BUFFER, self.specular_vbo)
        # # pass the new data for the vbo
        # glBufferData(GL_ARRAY_BUFFER, speculars_array.nbytes, speculars_array, GL_STATIC_DRAW)
        # # bind back to the default vbo
        # glBindBuffer(GL_ARRAY_BUFFER, 0)

        # shininesses_array = np.array(list(self.render_shininesses.values()), dtype=np.float32)
        # # bind the ambient vbo
        # glBindBuffer(GL_ARRAY_BUFFER, self.shininess_vbo)
        # # pass the new data for the vbo
        # glBufferData(GL_ARRAY_BUFFER, shininesses_array.nbytes, shininesses_array, GL_STATIC_DRAW)
        # # bind back to the default vbo
        # glBindBuffer(GL_ARRAY_BUFFER, 0)

        roughnesses_array = np.array(list(self.render_roughnesses.values()), dtype=np.float32)
        # bind the ambient vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.roughness_vbo)
        # pass the new data for the vbo
        # glBufferData(GL_ARRAY_BUFFER, roughnesses_array.nbytes, roughnesses_array, GL_STREAM_DRAW)
        glBufferSubData(GL_ARRAY_BUFFER, 0, roughnesses_array.nbytes, roughnesses_array)
        # bind back to the default vbo
        # glBindBuffer(GL_ARRAY_BUFFER, 0)

        metallicnesses_array = np.array(list(self.render_metallicnesses.values()), dtype=np.float32)
        # bind the ambient vbo
        glBindBuffer(GL_ARRAY_BUFFER, self.metallic_vbo)
        # pass the new data for the vbo
        # glBufferData(GL_ARRAY_BUFFER, metallicnesses_array.nbytes, metallicnesses_array, GL_STREAM_DRAW)
        glBufferSubData(GL_ARRAY_BUFFER, 0, metallicnesses_array.nbytes, metallicnesses_array)
        # bind back to the default vbo
        # glBindBuffer(GL_ARRAY_BUFFER, 0)
