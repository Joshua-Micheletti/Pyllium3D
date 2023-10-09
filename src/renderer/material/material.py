

class Material:
    def __init__(self,
                 name,
                 ambient_r = 0, ambient_g = 0, ambient_b = 0,
                 diffuse_r = 0, diffuse_g = 0, diffuse_b = 0,
                 specular_r = 0, specular_g = 0, specular_b = 0,
                 shininess = 1):
        self.name = name
        self.ambient = [ambient_r, ambient_g, ambient_b]
        self.diffuse = [diffuse_r, diffuse_g, diffuse_b]
        self.specular = [specular_r, specular_g, specular_b]
        self.shininess = shininess

        self.models = []

    def add_model(self, model):
        self.models.append(model)

    def set_ambient(self, r, g, b):
        self.ambient = [r, g, b]

    def set_diffuse(self, r, g, b):
        self.diffuse = [r, g, b]

    def set_specular(self, r, g, b):
        self.specular = [r, g, b]

    def set_shininess(self, s):
        self.shininess = s

    