# ruff: noqa: F403, F405

import numpy as np
from OpenGL.GL import *

from renderer.instance import Instance
from utils.messages import *


def new_instance(self, name, mesh, shader):
    # check if the mesh and shader fields have been provided
    if mesh == '':
        print_error("Couldn't create the instance, Mesh not set")
        return

    if shader == '':
        print_error("Couldn't create the instance, Shader not set")
        return

    # create a new instance object
    self.instances[name] = Instance()
    # get a reference to the newly created object
    instance = self.instances[name]

    # set the instance constants
    instance.mesh = mesh
    instance.shader = shader

    # intialize the instance
    self._initialize_instance(name)


# method to add a model to an instance
def add_model_to_instance(self, model, instance):
    model_name = model
    instance_name = instance
    model = self.models[model]
    instance = self.instances[instance]

    instance.models.append(model)

    model_mat_values = []

    for col in self.model_matrices[model_name]:
        for value in col:
            model_mat_values.append(value)

    instance.model_matrices = np.append(instance.model_matrices, model_mat_values)

    instance.ambients = np.append(instance.ambients, self.materials[model.material].ambient)
    instance.diffuses = np.append(instance.diffuses, self.materials[model.material].diffuse)
    instance.speculars = np.append(instance.speculars, self.materials[model.material].specular)
    instance.shininesses = np.append(instance.shininesses, self.materials[model.material].shininess)

    self.single_render_models.remove(model)

    model.in_instance = instance_name
    instance.to_update['model_matrices'] = True
    instance.to_update['ambients'] = True
    instance.to_update['diffuses'] = True
    instance.to_update['speculars'] = True
    instance.to_update['shininesses'] = True


def set_models_in_instance(self, models, instance_name):
    instance = self.instances[instance_name]
    instance.models = {}

    for model in models:
        instance.models[model] = self.models[model]
        self.single_render_models.remove(self.models[model])
        self.models[model].in_instance = instance_name

    self._initialize_instance(instance_name)


def remove_model_from_instance(self, model, instance):
    model = self.models[model]
    instance = self.instances[instance]

    instance.models.remove(model)
    # instance.model_matrices.pop(name)

    self.single_render_models.append(model)

    model.in_instance = ''
    instance.to_update['model_matrices'] = True


def set_instance_mesh(self, instance, mesh):
    if mesh != self.instances[instance].mesh:
        self.instances[instance].set_mesh(mesh, self.vertex_vbos[mesh], self.normal_vbos[mesh], self.uv_vbo[mesh])
    # self.instances[instance].mesh = mesh
    # self.instances[instance].to_update = True


def set_instance_shader(self, instance, shader):
    self.instances[instance].shader = shader
    # self.instances[instance].to_update = True


def set_model_to_render_in_instance(self, model, instance):
    self.instances[instance].models_to_render[model] = self.models[model]


# method to initialize an instance, might move this inside the instance object
def initialize_instance(self, name):
    instance = self.instances[name]

    # temporary list of model matrices
    # formatted_model_matrices = []

    # formatted_ambients = []
    # formatted_diffuses = []
    # formatted_speculars = []
    # formatted_shininesses = []
    # formatted_roughnesses = []
    # formatted_metallicnesses = []

    for name, model in instance.models.items():
        matrix = []
        for col in self.model_matrices[name]:
            for value in col:
                matrix.append(value)
        instance.model_matrices[name] = matrix

        material = self.materials[model.material]

        ambient = []
        ambient.append(material.ambient[0])
        ambient.append(material.ambient[1])
        ambient.append(material.ambient[2])
        instance.ambients[name] = ambient

        diffuse = []
        diffuse.append(material.diffuse[0])
        diffuse.append(material.diffuse[1])
        diffuse.append(material.diffuse[2])
        instance.diffuses[name] = diffuse

        specular = []
        specular.append(material.specular[0])
        specular.append(material.specular[1])
        specular.append(material.specular[2])
        instance.speculars[name] = specular

        shininess = []
        shininess.append(material.shininess)
        instance.shininesses[name] = shininess

        roughness = []
        roughness.append(material.roughness)
        instance.roughnesses[name] = roughness

        metallicness = []
        metallicness.append(material.metallic)
        instance.metallicnesses[name] = metallicness

    # formatted_ambients = np.array(formatted_ambients, dtype=np.float32)
    # formatted_diffuses = np.array(formatted_diffuses, dtype=np.float32)
    # formatted_speculars = np.array(formatted_speculars, dtype=np.float32)
    # formatted_shininesses = np.array(formatted_shininesses, dtype=np.float32)
    # formatted_roughnesses = np.array(formatted_roughnesses, dtype=np.float32)
    # formatted_metallicnesses = np.array(formatted_metallicnesses, dtype=np.float32)

    # convert the list into an array of 32bit floats
    # formatted_model_matrices = np.array(formatted_model_matrices, dtype=np.float32)
    # get the size in bits of an item in the matrices list

    # instance.model_matrices = formatted_model_matrices
    # instance.ambients = formatted_ambients
    # instance.diffuses = formatted_diffuses
    # instance.speculars = formatted_speculars
    # instance.shininesses = formatted_shininesses
    # instance.roughnesses = formatted_roughnesses
    # instance.metallicnesses = formatted_metallicnesses

    # if the model matrices vbo already exists, delete it
    # if instance.model_matrices_vbo != None:
    #     glDeleteBuffers(1, instance.model_matrices_vbo)

    model_matrices_array = np.array(list(instance.model_matrices.values()), dtype=np.float32).flatten()
    # generate a new buffer for the model matrices
    instance.model_matrices_vbo = glGenBuffers(1)
    # bind the new buffer
    glBindBuffer(GL_ARRAY_BUFFER, instance.model_matrices_vbo)
    # pass the data to the buffer
    glBufferData(
        GL_ARRAY_BUFFER,
        model_matrices_array.nbytes,
        model_matrices_array,
        GL_STREAM_DRAW,
    )
    # glBindBuffer(GL_ARRAY_BUFFER, 0)
    float_size = model_matrices_array.itemsize

    # if instance.ambient_vbo != None:
    #     instance.ambient_vbo = glGenBuffers(1)
    ambients_array = np.array(list(instance.ambients.values()), dtype=np.float32).flatten()
    instance.ambient_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, instance.ambient_vbo)
    glBufferData(GL_ARRAY_BUFFER, ambients_array.nbytes, ambients_array, GL_DYNAMIC_DRAW)

    diffuse_array = np.array(list(instance.diffuses.values()), dtype=np.float32).flatten()
    instance.diffuse_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, instance.diffuse_vbo)
    glBufferData(GL_ARRAY_BUFFER, diffuse_array.nbytes, diffuse_array, GL_DYNAMIC_DRAW)

    specular_array = np.array(list(instance.speculars.values()), dtype=np.float32).flatten()
    instance.specular_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, instance.specular_vbo)
    glBufferData(GL_ARRAY_BUFFER, specular_array.nbytes, specular_array, GL_DYNAMIC_DRAW)

    shininess_array = np.array(list(instance.shininesses.values()), dtype=np.float32)
    instance.shininess_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, instance.shininess_vbo)
    glBufferData(GL_ARRAY_BUFFER, shininess_array.nbytes, shininess_array, GL_DYNAMIC_DRAW)

    roughness_array = np.array(list(instance.roughnesses.values()), dtype=np.float32).flatten()
    instance.roughness_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, instance.roughness_vbo)
    glBufferData(GL_ARRAY_BUFFER, roughness_array.nbytes, roughness_array, GL_DYNAMIC_DRAW)

    metallicness_array = np.array(list(instance.metallicnesses.values()), dtype=np.float32).flatten()
    instance.metallic_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, instance.metallic_vbo)
    glBufferData(GL_ARRAY_BUFFER, metallicness_array.nbytes, metallicness_array, GL_DYNAMIC_DRAW)

    # if the vao already exists, delete it
    # if instance.vao != None:
    #     glDeleteVertexArrays(1, instance.vao)

    # create a new VAO
    instance.vao = glGenVertexArrays(1)
    # bind the newly created VAO
    glBindVertexArray(instance.vao)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebos[instance.mesh])

    # bind the vertex vbo of the mesh of the instance
    glBindBuffer(GL_ARRAY_BUFFER, self.vertex_vbos[instance.mesh])
    # enable the index 0 of the VAO
    glEnableVertexAttribArray(0)
    # link the VBO to the index 0 of the VAO and interpret it as 3 floats
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

    # bind the normals vbo of the mesh of the instance
    glBindBuffer(GL_ARRAY_BUFFER, self.normal_vbos[instance.mesh])
    # enable the index 1 of the VAO
    glEnableVertexAttribArray(1)
    # link the VBO to the index 1 of the VAO and interpret it as 3 floats
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

    # bind the uv vbo of the mesh of the instance
    glBindBuffer(GL_ARRAY_BUFFER, self.uv_vbos[instance.mesh])
    # enable the index 2 of the VAO
    glEnableVertexAttribArray(2)
    # link the VBO to the index 2 of the VAO and interpret it as 2 floats
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

    # bind the matrices vbo of the models of the instance
    glBindBuffer(GL_ARRAY_BUFFER, instance.model_matrices_vbo)
    # enable the index 3 of the VAO
    glEnableVertexAttribArray(3)
    # link the beginning of the VBO to the index 3 of the VAO and interpret it as 4 floats
    glVertexAttribPointer(3, 4, GL_FLOAT, GL_FALSE, float_size * 16, ctypes.c_void_p(0))

    # enable the index 4 of the VAO
    glEnableVertexAttribArray(4)
    # link the second column of the matrix to the index 4 of the VAO and interpret it as 4 floats
    glVertexAttribPointer(4, 4, GL_FLOAT, GL_FALSE, float_size * 16, ctypes.c_void_p(float_size * 4 * 1))

    # enable the index 5 of the VAO
    glEnableVertexAttribArray(5)
    # link the third column of the matrix to the index 5 of the VAO and intepret it as 4 floats
    glVertexAttribPointer(5, 4, GL_FLOAT, GL_FALSE, float_size * 16, ctypes.c_void_p(float_size * 4 * 2))

    # enable the index 6 of the VAO
    glEnableVertexAttribArray(6)
    # link the fourth column of the matrix to the index 6 of the VAO and intepret it as 4 floats
    glVertexAttribPointer(6, 4, GL_FLOAT, GL_FALSE, float_size * 16, ctypes.c_void_p(float_size * 4 * 3))

    # tell OpenGL that the indices 3, 4, 5 and 6 of the VAO need to change after every call
    glVertexBindingDivisor(3, 1)
    glVertexBindingDivisor(4, 1)
    glVertexBindingDivisor(5, 1)
    glVertexBindingDivisor(6, 1)

    glBindBuffer(GL_ARRAY_BUFFER, instance.ambient_vbo)
    glEnableVertexAttribArray(7)
    glVertexAttribPointer(7, 3, GL_FLOAT, GL_FALSE, float_size * 3, ctypes.c_void_p(0))

    glBindBuffer(GL_ARRAY_BUFFER, instance.diffuse_vbo)
    glEnableVertexAttribArray(8)
    glVertexAttribPointer(8, 3, GL_FLOAT, GL_FALSE, float_size * 3, ctypes.c_void_p(0))

    glBindBuffer(GL_ARRAY_BUFFER, instance.specular_vbo)
    glEnableVertexAttribArray(9)
    glVertexAttribPointer(9, 3, GL_FLOAT, GL_FALSE, float_size * 3, ctypes.c_void_p(0))

    glBindBuffer(GL_ARRAY_BUFFER, instance.shininess_vbo)
    glEnableVertexAttribArray(10)
    glVertexAttribPointer(10, 1, GL_FLOAT, GL_FALSE, float_size, ctypes.c_void_p(0))

    glBindBuffer(GL_ARRAY_BUFFER, instance.roughness_vbo)
    glEnableVertexAttribArray(11)
    glVertexAttribPointer(11, 1, GL_FLOAT, GL_FALSE, float_size, ctypes.c_void_p(0))

    glBindBuffer(GL_ARRAY_BUFFER, instance.metallic_vbo)
    glEnableVertexAttribArray(12)
    glVertexAttribPointer(12, 1, GL_FLOAT, GL_FALSE, float_size, ctypes.c_void_p(0))

    glVertexBindingDivisor(7, 1)
    glVertexBindingDivisor(8, 1)
    glVertexBindingDivisor(9, 1)
    glVertexBindingDivisor(10, 1)
    glVertexBindingDivisor(11, 1)
    glVertexBindingDivisor(12, 1)

    # bind to the default VAO
    glBindVertexArray(0)
