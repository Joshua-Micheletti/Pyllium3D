from renderer.RendererManager import RendererManager
import glm
import math
import glfw
import random

def setup():
    rm = RendererManager()

    count = 20

    rm.new_mesh("gally", "assets/models/gally.obj")
    rm.new_mesh("box", "assets/models/box.obj")
    rm.new_mesh("sphere", "assets/models/sphere.obj")
    rm.new_model("light", mesh="sphere", shader="lighting_instanced")
    rm.new_material("white", (0.2, 0.2, 0.2), (0.4, 0.4, 0.4), (0.8, 0.8, 0.8), 4.0)

    rm.place("light", 5, 5, 7.5)
    rm.scale("light", 0.25, 0.25, 0.25)
    rm.light_source = glm.vec3(5, 5, 7.5)

    for i in range(int(count / 10)):
        for j in range(10):
            rm.new_material("color" + str(i * 10 + j),
                            (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
                            (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
                            (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
                            random.uniform(1, 256))
            rm.new_model("entity" + str(i * 10 + j), mesh="box", shader="lighting_instanced", material="color" + str(i * 10 + j))
            rm.place("entity" + str(i * 10 + j), i * 3, 0, j * 3)


def update(dt):
    rm = RendererManager()
    time = dt / 1000.0
    # rm.place("light", math.cos(glfw.get_time() / 2) * time * 2 + rm.positions["light"].x, math.sin(glfw.get_time() / 2) * 6, math.sin(glfw.get_time() / 2) * time * 2 + rm.positions["light"].z)
    rm.light_source = rm.positions["light"]


