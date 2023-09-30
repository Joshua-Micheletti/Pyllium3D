
# class that represents the model to be rendered
class Model:
    # constructor method
    def __init__(self, mesh = "", texture = "", shader = ""):
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

        
        

    