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

    # ic(scene)

    rm = RendererManager()
    pw = PhysicsWorld()
    engine = Engine()

    _initialize_meshes(rm)
    _initialize_textures(rm)
    _initialize_materials(rm)
    _initialize_models(rm, pw, engine)


    # rm.new_model("sun", mesh="sphere_low", shader="white")
    # count = 100

    # rm.new_model("light", mesh="sphere_low", shader="white")

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

    # # engine.create_link("sphere", "light")

    # pw.new_body("floor", "plane", 0.0, orientation=[0, 0.707, -0.707, 0.0])
    # engine.create_link("floor", "floor")


def update(dt: float) -> None:
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
    rm.place_light("sun", *rm.positions["sun"])
    # rm.place_light("light", *rm.positions["light"])
    # rm.place_light("moon", *rm.positions["moon"])



def _initialize_meshes(rm: RendererManager) -> None:
    rm.new_json_mesh("gally", "assets/models/default/gally.json")
    rm.new_json_mesh("box", "assets/models/default/box.json")
    rm.new_json_mesh("quad", "assets/models/default/quad.json")
    rm.new_json_mesh("sphere", "assets/models/default/sphere.json")
    rm.new_json_mesh("sphere_low", "assets/models/default/sphere_low.json")


def _initialize_textures(rm: RendererManager) -> None:
    rm.new_texture("test", "assets/textures/uv-maptemplate.png")


def _initialize_materials(rm: RendererManager) -> None:
    # rough_white
    rm.new_material("rough_white", roughness=0.9, metallic=0.1)
    # white
    rm.new_material("white")
    # shiny_white
    rm.new_material("shiny_white", roughness=0.05, metallic=0.95)
    # rough_red
    rm.new_material(
        "rough_red",
        diffuse_r=1.0,
        diffuse_g=0.0,
        diffuse_b=0.0,
        roughness=0.9,
        metallic=0.1,
    )
    # rough_green
    rm.new_material(
        "rough_green",
        diffuse_r=0.0,
        diffuse_g=1.0,
        diffuse_b=0.0,
        roughness=0.9,
        metallic=0.1,
    )
    # rough_blue
    rm.new_material(
        "rough_blue",
        diffuse_r=0.0,
        diffuse_g=0.0,
        diffuse_b=1.0,
        roughness=0.9,
        metallic=0.1,
    )
    # red
    rm.new_material("red", diffuse_r=1.0, diffuse_g=0.0, diffuse_b=0.0)
    # green
    rm.new_material("green", diffuse_r=0.0, diffuse_g=1.0, diffuse_b=0.0)
    # blue
    rm.new_material("blue", diffuse_r=0.0, diffuse_g=0.0, diffuse_b=1.0)
    # shiny_red
    rm.new_material(
        "shiny_red",
        diffuse_r=1.0,
        diffuse_g=0.0,
        diffuse_b=0.0,
        roughness=0.1,
        metallic=0.9,
    )
    # shiny_green
    rm.new_material(
        "shiny_green",
        diffuse_r=0.0,
        diffuse_g=1.0,
        diffuse_b=0.0,
        roughness=0.1,
        metallic=0.9,
    )
    # shiny_blue
    rm.new_material(
        "shiny_blue",
        diffuse_r=0.0,
        diffuse_g=0.0,
        diffuse_b=1.0,
        roughness=0.1,
        metallic=0.9,
    )


def _initialize_models(rm: RendererManager, pw: PhysicsWorld, engine: Engine) -> None:
    test_mesh = "sphere"
    test_shader = "pbr"
    test_physics_body = "sphere"
    
    instance_entities = []
    
    rm.new_instance("instance", "sphere", "pbr_instanced")

    # sphere_rough_white
    rm.new_model(
        "sphere_rough_white", mesh=test_mesh, shader=test_shader, material="rough_white"
    )
    instance_entities.append("sphere_rough_white")
    # sphere_rough_red
    rm.new_model(
        "sphere_rough_red", mesh=test_mesh, shader=test_shader, material="rough_red"
    )
    instance_entities.append("sphere_rough_red")
    # sphere_rough_green
    rm.new_model(
        "sphere_rough_green", mesh=test_mesh, shader=test_shader, material="rough_green"
    )
    instance_entities.append("sphere_rough_green")
    # sphere_rough_blue
    rm.new_model(
        "sphere_rough_blue", mesh=test_mesh, shader=test_shader, material="rough_blue"
    )
    instance_entities.append("sphere_rough_blue")

    # sphere_white
    rm.new_model("sphere_white", mesh=test_mesh, shader=test_shader, material="white")
    instance_entities.append("sphere_white")
    # sphere_red
    rm.new_model("sphere_red", mesh=test_mesh, shader=test_shader, material="red")
    instance_entities.append("sphere_red")
    # sphere_green
    rm.new_model("sphere_green", mesh=test_mesh, shader=test_shader, material="green")
    instance_entities.append("sphere_green")
    # sphere_blue
    rm.new_model("sphere_blue", mesh=test_mesh, shader=test_shader, material="blue")
    instance_entities.append("sphere_blue")

    # sphere_shiny_white
    rm.new_model(
        "sphere_shiny_white", mesh=test_mesh, shader=test_shader, material="shiny_white"
    )
    instance_entities.append("sphere_shiny_white")
    # sphere_shiny_red
    rm.new_model(
        "sphere_shiny_red", mesh=test_mesh, shader=test_shader, material="shiny_red"
    )
    instance_entities.append("sphere_shiny_red")
    # sphere_shiny_green
    rm.new_model(
        "sphere_shiny_green", mesh=test_mesh, shader=test_shader, material="shiny_green"
    )
    instance_entities.append("sphere_shiny_green")
    # sphere_shiny_blue
    rm.new_model(
        "sphere_shiny_blue", mesh=test_mesh, shader=test_shader, material="shiny_blue"
    )
    instance_entities.append("sphere_shiny_blue")

    rm.move("sphere_rough_white", -4, 5, 0)
    if test_mesh == "sphere":
        rm.scale("sphere_rough_white", 2, 2, 2)
    pw.new_body("p_sphere_rough_white", shape=test_physics_body, position=[-4, 5, 0], mass=1)
    engine.create_link("p_sphere_rough_white", "sphere_rough_white")
    
    rm.move("sphere_rough_red", -1.333, 5, 0)
    if test_mesh == "sphere":
        rm.scale("sphere_rough_red", 2, 2, 2)
    pw.new_body("p_sphere_rough_red", shape=test_physics_body, position=[-1.333, 5, 0], mass=1)
    engine.create_link("p_sphere_rough_red", "sphere_rough_red")
    
    rm.move("sphere_rough_green", 1.333, 5, 0)
    if test_mesh == "sphere":
        rm.scale("sphere_rough_green", 2, 2, 2)
    pw.new_body("p_sphere_rough_green", shape=test_physics_body, position=[1.333, 5, 0], mass=1)
    engine.create_link("p_sphere_rough_green", "sphere_rough_green")
    
    rm.move("sphere_rough_blue", 4, 5, 0)
    if test_mesh == "sphere":
        rm.scale("sphere_rough_blue", 2, 2, 2)
    pw.new_body("p_sphere_rough_blue", shape=test_physics_body, position=[4, 5, 0], mass=1)
    engine.create_link("p_sphere_rough_blue", "sphere_rough_blue")

    rm.move("sphere_white", -4.01, 7, 0.01)
    if test_mesh == "sphere":
        rm.scale("sphere_white", 2, 2, 2)
    pw.new_body("p_sphere_white", shape=test_physics_body, position=[-4.01, 7, 0.01], mass=1)
    engine.create_link("p_sphere_white", "sphere_white")
    
    rm.move("sphere_red", -1.3334, 7, 0.01)
    if test_mesh == "sphere":
        rm.scale("sphere_red", 2, 2, 2)
    pw.new_body("p_sphere_red", shape=test_physics_body, position=[-1.3334, 7, 0.01], mass=1)
    engine.create_link("p_sphere_red", "sphere_red")
    
    rm.move("sphere_green", 1.3334, 7, 0.01)
    if test_mesh == "sphere":
        rm.scale("sphere_green", 2, 2, 2)
    pw.new_body("p_sphere_green", shape=test_physics_body, position=[1.3334, 7, 0.01], mass=1)
    engine.create_link("p_sphere_green", "sphere_green")
    
    rm.move("sphere_blue", 4.01, 7, 0.01)
    if test_mesh == "sphere":
        rm.scale("sphere_blue", 2, 2, 2)
    pw.new_body("p_sphere_blue", shape=test_physics_body, position=[4.01, 7, 0.01], mass=1)
    engine.create_link("p_sphere_blue", "sphere_blue")

    rm.move("sphere_shiny_white", -4.02, 9, -0.01)
    if test_mesh == "sphere":
        rm.scale("sphere_shiny_white", 2, 2, 2)
    pw.new_body("p_sphere_shiny_white", shape=test_physics_body, position=[-4.02, 9, -0.01], mass=1)
    engine.create_link("p_sphere_shiny_white", "sphere_shiny_white")
    
    rm.move("sphere_shiny_red", -1.3332, 9, -0.01)
    if test_mesh == "sphere":
        rm.scale("sphere_shiny_red", 2, 2, 2)
    pw.new_body("p_sphere_shiny_red", shape=test_physics_body, position=[-1.3332, 9, -0.01], mass=1)
    engine.create_link("p_sphere_shiny_red", "sphere_shiny_red")
    
    rm.move("sphere_shiny_green", 1.3332, 9, -0.01)
    if test_mesh == "sphere":
        rm.scale("sphere_shiny_green", 2, 2, 2)
    pw.new_body("p_sphere_shiny_green", shape=test_physics_body, position=[1.3332, 9, -0.01], mass=1)
    engine.create_link("p_sphere_shiny_green", "sphere_shiny_green")
    
    rm.move("sphere_shiny_blue", 4.02, 9, -0.01)
    if test_mesh == "sphere":
        rm.scale("sphere_shiny_blue", 2, 2, 2)
    pw.new_body("p_sphere_shiny_blue", shape=test_physics_body, position=[4.02, 9, -0.01], mass=1)
    engine.create_link("p_sphere_shiny_blue", "sphere_shiny_blue")


    rm.new_model("floor", mesh="quad", shader="pbr", material="rough_white")
    rm.new_model("sun", mesh="sphere_low", shader="white")

    rm.rotate("floor", -90, 0, 0)
    rm.move("floor", 0, -1, 0)
    rm.scale("floor", 20, 20, 1)
    
    pw.new_body("p_floor", "plane", 0.0, orientation=[-0.707, 0, 0, 0.707])
    pw.new_body("wall_-x", "plane", 0.0, position=[-6, 0, 0], orientation=[0, 0.707, 0, 0.707])
    pw.new_body("wall_+x", "plane", 0.0, position=[6, 0, 0], orientation=[0, -0.707, 0, 0.707])
    pw.new_body("wall_-z", "plane", 0.0, position=[0, 0, -6], orientation=[0, 0, 1, 0])
    pw.new_body("wall_+z", "plane", 0.0, position=[0, 0, 6], orientation=[0, 1, 0, 0])
    engine.create_link("p_floor", "floor")

    rm.move("sun", 3, 10, 3)
    
    rm.update()
    # rm.set_models_in_instance(instance_entities, "instance")
