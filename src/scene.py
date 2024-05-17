from renderer.renderer_manager.renderer_manager import RendererManager
from physics.physics_world import PhysicsWorld
from engine.engine import Engine
import glm
import random
import math
import glfw

from utils import Timer
from utils import *
from utils import Config

@timeit()
def setup():
    scene = Config().scene
    
    ic(scene)
    
    rm = RendererManager()
    pw = PhysicsWorld()
    engine = Engine()
    
    rm.new_json_mesh("gally", "assets/models/default/gally.json")
    rm.new_json_mesh("box", "assets/models/default/box.json")
    rm.new_json_mesh("quad", "assets/models/default/quad.json")
    rm.new_json_mesh("sphere", "assets/models/default/sphere.json")
    rm.new_json_mesh("sphere_low", "assets/models/default/sphere_low.json")

    
    rm.new_model("test", mesh="sphere", shader="pbr")

    # rm.new_texture("test", "assets/textures/uv-maptemplate.png")
    # rm.new_model("light", mesh="sphere_low", shader="white")
    # rm.new_model("sun", mesh="sphere_low", shader="white")

    # rm.new_model("test", mesh="sphere", shader="pbr")
    
    # rm.new_material("white", *(0.2, 0.2, 0.2), *(0.4, 0.4, 0.4), *(0.8, 0.8, 0.8), 4.0)
    # rm.new_material("full_white", *(1.0, 1.0, 1.0), *(1.0, 1.0, 1.0), *(1.0, 1.0, 1.0), 4.0, 0.2, 0.0)

    # rm.new_material("911", *(0.0, 0.0, 0.0), *(0.1, 0.5, 0.1), *(0.0, 0.0, 0.0), 1, 0.1, 0.9)

    # rm.scale("light", 0.5, 0.5, 0.5)

    # rm.place("light", 4, 4, 4)
    # rm.place("sun", 0, 10, 0)

    # rm.new_light("light_1", (0, 0, 0), (1, 0, 0), 8)
    # rm.new_light("light_2", (0, 0, 0), (0, 1, 0), 8)
    # rm.new_light("light_3", (0, 0, 0), (0, 0, 1), 8)
    

    # rm.new_material("red_wall",   1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 128)
    # rm.new_material("green_wall", 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 128)
    # rm.new_material("blue_wall",  0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 128)

    # rm.new_model("floor", mesh="quad", shader="pbr", material="full_white")

    # rm.rotate("floor", 270, 0, 0)
    # rm.place("floor", 0, -1, 5)
    # rm.scale("floor", 40, 40, 1)

    # entities = []

    # rm.new_instance("colored_boxes", "sphere", "pbr_instanced")

    # entities = []
    # pw.create_sphere_shape("sphere")
    # pw.create_box_shape("box", [0.5, 0.5, 0.5])

    # entities = []

    # distance = 20

    # for i in range(int(count / 10)):
    #     for j in range(10):
    #         name = "entity_box" + str(i * 10 + j)
    #         rm.new_material("color_box" + str(i * 10 + j),
    #                         *(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
    #                         *(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
    #                         *(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
    #                         random.uniform(1, 256),
    #                         random.uniform(0, 1),
    #                         random.uniform(0, 1))
            
    #         rm.new_model("entity_box" + str(i * 10 + j), mesh="box", shader="pbr", material="color_box" + str(i * 10 + j))
    #         rm.scale("entity_box" + str(i * 10 + j), 0.5, 0.5, 0.5)
    #         rm.place(name, (random.random() - 0.5) * distance, (random.random() + 0.1) * distance, (random.random() - 0.5) * distance)
    #         pw.new_body("entity_box" + str(i * 10 + j), "sphere", 1.0, position=[(random.random() - 0.5) * distance, (random.random() + 0.1) * distance, (random.random() - 0.5) * distance])
    #         engine.create_link("entity_box" + str(i * 10 + j), "entity_box" + str(i * 10 + j))
    #         entities.append("entity_box" + str(i * 10 + j))

    #         # if i * 10 + j % 2 == 0:
    #         #     # rm.instances["colored_boxes"].models_to_render.append(name)
    #         #     rm.set_model_to_render_in_instance(name, "colored_boxes")
    
    # rm.update()
    # rm.set_models_in_instance(entities, "colored_boxes")

    # engine = Engine()

    # engine.create_link("sphere", "light")

    # pw.new_body("floor", "plane", 0.0, orientation=[0, 0.707, -0.707, 0.0])
    # engine.create_link("floor", "floor")

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
    # rm.light_source.place(*rm.positions["light"])
    # rm.place_light("main", *rm.positions["light"])
    # rm.place_light("light_1", *rm.positions["light_1"])
    # rm.place_light("light_2", *rm.positions["light_2"])
    # rm.place_light("light_3", *rm.positions["light_3"])
    # rm.place_light("sun", *rm.positions["sun"])
    # rm.place_light("light", *rm.positions["light"])
    # rm.place_light("moon", *rm.positions["moon"])
