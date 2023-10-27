import glm

class Light:
    def __init__(self):
        self.position = glm.vec3(0.0)
        self.strength = 8.0
        self.color = glm.vec3(1.0, 1.0, 1.0)

    def set_strength(self, s):
        self.strength = s

    def place(self, x, y, z):
        self.position = glm.vec3(x, y, z)
    
    def set_color(self, r, g, b):
        self.color = glm.vec3(1.0, 1.0, 1.0)