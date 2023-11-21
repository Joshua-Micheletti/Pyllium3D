from renderer.renderer_manager import RendererManager
from physics.physics_world import PhysicsWorld
from engine.engine import Engine
import glm
import random
import math
import glfw

from utils.timer import Timer
from utils.messages import *

def setup():
    timer = Timer()

    rm = RendererManager()
    pw = PhysicsWorld()
    engine = Engine()

    count = 5000

    # rm.new_shader("cel", "assets/shaders/cel_shading/cel_shading.vert", "assets/shaders/cel_shading/cel_shading.frag")
    # rm.new_shader("pbr_texture", "assets/shaders/pbr_texture/pbr_texture.vert", "assets/shaders/pbr_texture/pbr_texture.frag")

    rm.new_json_mesh("gally", "assets/models/default/gally.json")
    rm.new_json_mesh("box", "assets/models/default/box.json")
    rm.new_json_mesh("quad", "assets/models/default/quad.json")
    # # rm.new_mesh("charmander", "assets/models/charmander/charmander.obj")
    # rm.new_json_mesh("charmander", "assets/models/charmander/charmander.json")
    rm.new_json_mesh("sphere", "assets/models/default/sphere.json")
    rm.new_json_mesh("sphere_low", "assets/models/default/sphere_low.json")
    # rm.new_mesh("lamppost", "assets/models/lamppost/lamppost.obj")
    # rm.new_json_mesh("pumpkin", "assets/models/pumpkin/pumpkin.json")

    rm.new_texture("test", "assets/textures/uv-maptemplate.png")
    # # rm.new_mesh("quad", "assets/models/default/quad.obj")
    rm.new_model("light", mesh="sphere_low", shader="white")
    rm.new_model("light_1", mesh="sphere_low", shader="white")
    rm.new_model("light_2", mesh="sphere_low", shader="white")
    rm.new_model("light_3", mesh="sphere_low", shader="white")
    rm.new_model("sun", mesh="sphere_low", shader="white")
    rm.new_material("white", *(0.2, 0.2, 0.2), *(0.4, 0.4, 0.4), *(0.8, 0.8, 0.8), 4.0)
    rm.new_material("full_white", *(1.0, 1.0, 1.0), *(1.0, 1.0, 1.0), *(1.0, 1.0, 1.0), 4.0, 0.2, 0.0)

    rm.scale("light", 0.5, 0.5, 0.5)
    rm.scale("light_1", 0.2, 0.2, 0.2)
    rm.scale("light_2", 0.2, 0.2, 0.2)
    rm.scale("light_3", 0.2, 0.2, 0.2)

    rm.place("light", 4, 4, 4)
    rm.place("sun", 0, 25, 0)
    # # rm.scale("light", 0.25, 0.25, 0.25)
    # # rm.light_source = glm.vec3(5, 5, 5)

    rm.new_model("cel", mesh="gally", shader="pbr", material="white")
    rm.place("cel", 5, 3, 5)

    rm.new_light("light_1", (0, 0, 0), (1, 0, 0), 0)
    rm.new_light("light_2", (0, 0, 0), (0, 1, 0), 0)
    rm.new_light("light_3", (0, 0, 0), (0, 0, 1), 0)
    

    rm.new_material("red_wall",   1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 128)
    rm.new_material("green_wall", 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 128)
    rm.new_material("blue_wall",  0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 128)

    # rm.new_model("red_wall", mesh="quad", shader="pbr", material="red_wall")
    # rm.new_model("green_wall", mesh="quad", shader="pbr", material="green_wall")
    # rm.new_model("blue_wall", mesh="quad", shader="pbr", material="blue_wall")
    rm.new_model("floor", mesh="quad", shader="pbr", material="full_white")

    rm.new_model("billboard", mesh="quad", shader="billboard")

    # rm.place("red_wall", 10, 0, -2)
    # rm.scale("red_wall", 10, 10, 10)
    # rm.place("green_wall", 0, 0, 0)
    # rm.rotate("green_wall", 0, 90, 0)
    # rm.scale("green_wall", 10, 10, 10)
    # rm.place("blue_wall", 10, 0, 10)
    # rm.scale("blue_wall", 10, 10, 10)
    # rm.rotate("blue_wall", 0, 180, 0)

    rm.rotate("floor", 270, 0, 0)
    rm.place("floor", 0, -1, 5)
    rm.scale("floor", 40, 40, 1)

    # rm.new_material("orange", diffuse_r=1, diffuse_g=0.5, diffuse_b=0, metallic=0.1, roughness=0.3)
    # rm.new_model("pumpkin", mesh="pumpkin", shader="pbr", material="orange")
    # rm.scale("pumpkin", 0.01, 0.01, 0.01)

    # rm.new_instance("test_materials", "sphere", "pbr_instanced")

    entities = []

    # for i in range(5):
    #     for j in range(5):
    #         name = "pbr_" + str(i) + str(j)
    #         rm.new_material(name,
    #                         diffuse_r = 1.0, diffuse_g = 0.0, diffuse_b = 0.0,
    #                         roughness = i / 5,
    #                         metallic = j / 5)

    #         rm.new_model(name,
    #                      mesh = "sphere",
    #                      shader = "pbr",
    #                      material = "pbr_" + str(i) + str(j))
            
    #         rm.place(name, 5, (i + 1) * 2, j * 2)

    #         entities.append(name)

    # rm.set_models_in_instance(entities, "test_materials")

    # # rm.new_model("second_sphere", mesh="sphere", shader="lighting_instanced")

    rm.new_instance("colored_entities", "sphere", "pbr_instanced")
    rm.new_instance("colored_boxes", "box", "pbr_instanced")

    entities = []
    pw.create_sphere_shape("sphere")
    pw.create_box_shape("box", [0.5, 0.5, 0.5])

    # for i in range(int(count / 10)):
    #     for j in range(10):
    #         rm.new_material("color" + str(i * 10 + j),
    #                         *(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
    #                         *(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
    #                         *(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
    #                         random.uniform(1, 256),
    #                         random.uniform(0, 1),
    #                         random.uniform(0, 1))
    #         rm.new_model("entity" + str(i * 10 + j), mesh="box", shader="lighting", material="color" + str(i * 10 + j))
    #         pw.new_body("entity" + str(i * 10 + j), "sphere", 1.0, position=[i*3, 1, j*3])

    #         engine.create_link("entity" + str(i * 10 + j), "entity" + str(i * 10 + j))

    #         rm.place("entity" + str(i * 10 + j), i * 3, 1, j * 3)
    #         # rm.place("entity" + str(i * 10 + j), 1, 0, 1)
    #         # rm.add_model_to_instance("entity" + str(i * 10 + j), "colored_entities")
    #         entities.append("entity" + str(i * 10 + j))

    # for i in range(int(count / 10)):
    #     for j in range(10):
    #         name = "entity" + str(i * 10 + j)
    #         rm.new_material("color" + str(i * 10 + j),
    #                         *(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
    #                         *(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
    #                         *(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
    #                         random.uniform(1, 256),
    #                         random.uniform(0, 1),
    #                         random.uniform(0, 1))
            
    #         rm.new_model(name, mesh="box", shader="lighting", material="color" + str(i * 10 + j))
    #         rm.place(name, (random.random() - 0.5) * 10, (random.random() + 0.1) * 10, (random.random() - 0.5) * 10)
    #         pw.new_body("entity" + str(i * 10 + j), "sphere", 1.0, position=[(random.random() - 0.5) * 10, (random.random() + 0.1) * 10, (random.random() - 0.5) * 10])
    #         engine.create_link("entity" + str(i * 10 + j), "entity" + str(i * 10 + j))
    #         entities.append("entity" + str(i * 10 + j))
    
    # rm.update()
    # rm.set_models_in_instance(entities, "colored_entities")

    entities = []

    for i in range(int(count / 10)):
        for j in range(10):
            name = "entity_box" + str(i * 10 + j)
            rm.new_material("color_box" + str(i * 10 + j),
                            *(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
                            *(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
                            *(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
                            random.uniform(1, 256),
                            random.uniform(0, 1),
                            random.uniform(0, 1))
            
            rm.new_model("entity_box" + str(i * 10 + j), mesh="box", shader="lighting", material="color_box" + str(i * 10 + j))
            rm.scale("entity_box" + str(i * 10 + j), 0.5, 0.5, 0.5)
            rm.place(name, (random.random() - 0.5) * 10, (random.random() + 0.1) * 10, (random.random() - 0.5) * 10)
            # pw.new_body("entity_box" + str(i * 10 + j), "box", 1.0, position=[(random.random() - 0.5) * 10, (random.random() + 0.1) * 10, (random.random() - 0.5) * 10])
            # engine.create_link("entity_box" + str(i * 10 + j), "entity_box" + str(i * 10 + j))
            entities.append("entity_box" + str(i * 10 + j))
    
    rm.update()
    rm.set_models_in_instance(entities, "colored_boxes")

    

    # rm.new_model("lamppost", mesh="lamppost", shader="pbr")

    # setup_pumpkin_patch()
    engine = Engine()

    engine.create_link("sphere", "light")

    pw.new_body("floor", "plane", 0.0, orientation=[0, 0.707, -0.707, 0.0])
    engine.create_link("floor", "floor")

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
    # rm.light_source.place(*rm.positions["light"])
    rm.place_light("main", *rm.positions["light"])
    # rm.place_light("light_1", *rm.positions["light_1"])
    # rm.place_light("light_2", *rm.positions["light_2"])
    # rm.place_light("light_3", *rm.positions["light_3"])
    rm.place_light("sun", *rm.positions["sun"])
    # rm.place_light("light", *rm.positions["light"])
    # rm.place_light("moon", *rm.positions["moon"])

def setup_pumpkin_patch():
    rm = RendererManager()

    rm.new_shader("pbr_texture", "assets/shaders/pbr_texture/pbr_texture.vert", "assets/shaders/pbr_texture/pbr_texture.frag")

    rm.new_mesh("lamppost", "assets/models/lamppost/lamppost.obj")
    rm.new_json_mesh("quad", "assets/models/default/quad.json")
    rm.new_json_mesh("pumpkin", "assets/models/pumpkin/pumpkin.json")
    rm.new_json_mesh("sphere_low", "assets/models/default/sphere_low.json")

    rm.new_texture("grass", "assets/textures/grass.jpg")

    rm.new_material("pumpkin", diffuse_r=1.0, diffuse_g=0.35, diffuse_b=0, roughness=0.2, metallic=0.0)
    rm.new_material("lamppost", diffuse_r=0.1, diffuse_g=0.1, diffuse_b=0.1, roughness=0.2, metallic=0.9)

    rm.new_model("lamppost", mesh="lamppost", shader="pbr", material="lamppost")
    rm.new_model("floor", mesh="quad", shader="pbr_texture", texture="grass")
    rm.new_model("moon", mesh="sphere_low", shader="white")
    rm.new_model("light", mesh="sphere_low", shader="white")
    rm.new_model("pumpkin", mesh="pumpkin", shader="pbr", material="pumpkin")

    rm.new_light("light", (0, 0, 0), (0.8, 0.6, 0), 2)
    rm.new_light("moon", (0, 0, 0), (1.0, 1.0, 1.0), 25)
    
    rm.scale("lamppost", 0.15, 0.15, 0.15)
    rm.scale("floor", 10, 10, 1)
    rm.scale("pumpkin", 0.004, 0.004, 0.004)
    rm.scale("light", 0.0, 0.0, 0.0)

    
    rm.place("light", -0.3, 1.4, 0.0)
    rm.place("moon", 0, 100, 0)

    rm.rotate("floor", 270, 0, 0)

