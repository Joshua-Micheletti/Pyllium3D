from renderer.RendererManager import RendererManager
import glm

def setup():
    rm = RendererManager()

    count = 200

    rm.new_mesh("sphere", "models/sphere.obj", count=count)
    rm.new_mesh("light", "models/sphere.obj")

    rm.move("light", 5, 5, 7.5)
    rm.scale("light", 0.25, 0.25, 0.25)
    rm.light_source = glm.vec3(5, 5, 7.5)

    for i in range(int(count / 10)):
        for j in range(10):
            rm.move("sphere" + str(i * 10 + j), i, 0, j)