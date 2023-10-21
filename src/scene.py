from renderer.RendererManager import RendererManager
import glm
import random
import math
import glfw

from utils.Timer import Timer
from utils.messages import *

def setup():
    timer = Timer()

    rm = RendererManager()

    count = 200

    rm.new_shader("cel", "assets/shaders/cel_shading/cel_shading.vert", "assets/shaders/cel_shading/cel_shading.frag")

    # rm.new_mesh("gally", "assets/models/default/gally.obj")
    rm.new_mesh("box", "assets/models/default/box.obj")
    # rm.new_mesh("charmander", "assets/models/charmander/charmander.obj")
    # rm.new_mesh("sphere", "assets/models/default/sphere.obj")
    rm.new_mesh("sphere_low", "assets/models/default/sphere_low.obj")
    # rm.new_mesh("quad", "assets/models/default/quad.obj")
    rm.new_model("light", mesh="sphere_low", shader="white")
    rm.new_material("white", *(0.2, 0.2, 0.2), *(0.4, 0.4, 0.4), *(0.8, 0.8, 0.8), 4.0)

    rm.place("light", 0, 1, -1)
    # rm.scale("light", 0.25, 0.25, 0.25)
    rm.light_source = glm.vec3(5, 5, 5)

    rm.new_model("cel", mesh="sphere_low", shader="cel", material="white")
    rm.place("cel", 2, 2, 2)

    # rm.new_model("second_sphere", mesh="sphere", shader="lighting_instanced")

    rm.new_instance("colored_entities", "box", "lighting_instanced")

    entities = []

    for i in range(int(count / 10)):
        for j in range(10):
            rm.new_material("color" + str(i * 10 + j),
                            *(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
                            *(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
                            *(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
                            random.uniform(1, 256))
            rm.new_model("entity" + str(i * 10 + j), mesh="box", shader="lighting", material="color" + str(i * 10 + j))
            rm.place("entity" + str(i * 10 + j), i * 3, 0, j * 3)
            # rm.place("entity" + str(i * 10 + j), 1, 0, 1)
            # rm.add_model_to_instance("entity" + str(i * 10 + j), "colored_entities")
            entities.append("entity" + str(i * 10 + j))
    
    rm.update()

    rm.set_models_in_instance(entities, "colored_entities")

    # rm.add_post_processing_shader("post_processing/inverted_colors")
    # rm.add_post_processing_shader("post_processing/black_white")
    # rm.add_post_processing_shader("post_processing/inverted_colors")
    # rm.add_post_processing_shader("post_processing/inverted_colors")

    print_success("Initialized Scene in " + str(round(timer.elapsed() / 1000, 2)) + "s")

def update(dt):
    rm = RendererManager()
    time = dt / 1000.0

    # i = 0

    # for model in rm.instances["colored_entities"].models:
    #     rm.move(model.name, time, time, time)
    #     rm.rotate(model.name, time, time, time)
    #     rm.scale(model.name, time * 3, time * 3, time * 3)

    #     i += 1
    #     if i == 2000:
    #         break

    # for model in rm.models.values():
    #     rm.move(model.name, time, time, time)

    # rm.place("light", math.cos(glfw.get_time() / 2) * time * 2 + rm.positions["light"].x, math.sin(glfw.get_time() / 2) * 6, math.sin(glfw.get_time() / 2) * time * 2 + rm.positions["light"].z)
    rm.light_source = rm.positions["light"]


