from renderer.RendererManager import RendererManager
import glm
import math
import glfw

def setup():
    rm = RendererManager()

    count = 600

    rm.new_mesh("sphere", "assets/models/gally.obj")
    rm.new_model("light", "sphere", "white")
    rm.new_model("sphere", "sphere", "lighting", "", count)

    rm.place("light", 5, 5, 7.5)
    rm.scale("light", 0.25, 0.25, 0.25)
    rm.light_source = glm.vec3(5, 5, 7.5)

    for i in range(int(count / 10)):
        for j in range(10):
            rm.place("sphere" + str(i * 10 + j), i, 0, j)

    # rm.new_texture("test", "assets/textures/uv-maptemplate.jpg")

def update(dt):
    rm = RendererManager()
    time = dt / 1000.0
    rm.place("light", math.cos(glfw.get_time()) * time * 2 + rm.positions["light"].x, math.sin(glfw.get_time()) * 6, math.sin(glfw.get_time()) * time * 2 + rm.positions["light"].z)
    rm.light_source = rm.positions["light"]

