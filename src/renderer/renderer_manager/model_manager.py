import glm
from renderer.model.model import Model

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