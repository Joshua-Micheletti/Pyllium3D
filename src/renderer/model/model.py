
# class that represents the model to be rendered
class Model:
    # constructor method
    def __init__(self, name = "", mesh = "default", texture = "default", shader = "default", material = "default"):
        if len(name) != 0:
            self.name = name
        else:
            self.name = None

        if len(mesh) != 0:
            self.mesh = mesh
        else:
            self.mesh = None
        
        if len(texture) != 0:
            self.texture = texture
        else:
            self.texture = None
        
        if len(shader) != 0:
            self.shader = shader
        else:
            self.shader = None

        if len(material) != 0:
            self.material = material
        else:
            self.material = None

        self.in_instance = ""

        
        

    