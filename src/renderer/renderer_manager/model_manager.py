import glm
from renderer.model.model import Model
from utils.messages import *

def new_model(self, name, mesh = "default", shader = "default", texture = "default", material = "default", count = 1):
    # keep track of the original name of the model (in case there is mulitple counts)
    original_name = name

    # iterate through all the new models
    for i in range(count):
        # if there is more than one model to be created
        if count != 1:
            # append a number to the name
            name = original_name + str(i)

        # create a new model object
        self.models[name] = Model(name, mesh, texture, shader, material)
        self.materials[material].add_model(self.models[name])

        self.single_render_models.append(self.models[name])

        # initialize the transformation variables for the new mesh
        self.positions[name] = glm.vec3(0.0)
        self.rotations[name] = glm.vec3(0.0)
        self.scales[name] = glm.vec3(1.0)
        self.model_matrices[name] = glm.mat4(1.0)
        
        self.model_bounding_sphere_center[name] = self.bounding_sphere_center[self.models[name].mesh] + self.positions[name]
        self.model_bounding_sphere_radius[name] = self.bounding_sphere_radius[self.models[name].mesh]
        

# method to place the mesh in a specific spot
def place(self, name, x, y, z):
    self.positions[name] = glm.vec3(x, y, z)
    self.changed_models[name] = True
    # self._calculate_model_matrix(name)
    # self._check_instance_update(name)     

# method to move a mesh by a certain vector
def move(self, name, x, y, z):
    self.positions[name] += glm.vec3(x, y, z)
    self.changed_models[name] = True
    # self._calculate_model_matrix(name)
    # self._check_instance_update(name)

# method to rotate the mesh
def rotate(self, name, x, y, z):
    self.rotations[name] = glm.vec3(x, y, z)
    self.changed_models[name] = True
    # self._calculate_model_matrix(name)
    # self._check_instance_update(name)

# method to scale the mesh
def scale(self, name, x, y, z):
    self.scales[name] = glm.vec3(x, y, z)
    self.changed_models[name] = True
    # self._calculate_model_matrix(name)
    # self._check_instance_update(name)

def place_light(self, name, x, y, z):
    if name in self.lights:
        if x != self.light_positions[self.lights[name] * 3 + 0] or y != self.light_positions[self.lights[name] * 3 + 1] or z != self.light_positions[self.lights[name] * 3 + 2]:
            self.light_positions[self.lights[name] * 3 + 0] = x
            self.light_positions[self.lights[name] * 3 + 1] = y
            self.light_positions[self.lights[name] * 3 + 2] = z
            # self.render_states["shadow_map"] = True
    else:
        print_error(f"Light '{name}' not found")

# method to calculate the model matrix after a transformation
def calculate_model_matrix(self, name):
    # reset the model matrix
    self.model_matrices[name] = glm.mat4(1)
    # calculate the translation
    self.model_matrices[name] = glm.translate(self.model_matrices[name], self.positions[name])
    # calculate the rotation by every axis
    self.model_matrices[name] = glm.rotate(self.model_matrices[name], glm.radians(self.rotations[name].x), glm.vec3(1.0, 0.0, 0.0))
    self.model_matrices[name] = glm.rotate(self.model_matrices[name], glm.radians(self.rotations[name].y), glm.vec3(0.0, 1.0, 0.0))
    self.model_matrices[name] = glm.rotate(self.model_matrices[name], glm.radians(self.rotations[name].z), glm.vec3(0.0, 0.0, 1.0))
    
    
    # calculate the scale
    scale = self.scales[name]
    self.model_matrices[name] = glm.scale(self.model_matrices[name], scale)

    max_scale = max(max(scale.x, scale.y), scale.z)

    self.model_bounding_sphere_center[name] = self.bounding_sphere_center[self.models[name].mesh] + self.positions[name]
    self.model_bounding_sphere_radius[name] = self.bounding_sphere_radius[self.models[name].mesh] * max_scale

# method to check if an instance should be updated after a transformation
def check_instance_update(self, name):
    if self.models[name].in_instance == "":
        return
    
    for instance in self.instances.values():
        if self.models[name] in instance.models.values():
            instance.to_update["model_matrices"] = True
            instance.change_model_matrix(self.models[name], self.model_matrices[name])
