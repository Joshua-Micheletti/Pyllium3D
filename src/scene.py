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
    """function to setup the scene"""
    
    scene = Config().scene

    # ic(scene)

    rm = RendererManager()
    pw = PhysicsWorld()
    engine = Engine()

    _initialize_meshes(rm, scene.get("meshes"))
    _initialize_textures(rm, scene.get("textures"))
    _initialize_materials(rm, scene.get("materials"))
    _initialize_models(rm, pw, engine, scene.get("models"))
    _initialize_physics(pw, scene.get("physics_bodies"))
    _initialize_links(engine, scene.get("links"))


def update(dt: float) -> None:
    """function to update the state of the entities

    Args:
        dt (float): time that passed since the last update
    """
    
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


def _initialize_meshes(rm: RendererManager, meshes: dict) -> None:
    """initialize all the meshes passed as an argument

    Args:
        rm (RendererManager): RendererManager object reference
        meshes (dict): dictionary of paths to mesh files
    """
    
    for key, value in meshes.items():
        rm.new_json_mesh(key, value)


def _initialize_textures(rm: RendererManager, textures: dict) -> None:
    rm.new_texture("test", "assets/textures/uv-maptemplate.png")


def _initialize_materials(rm: RendererManager, materials: dict) -> None:
    for key, value in materials.items():
        rm.new_material(
            key,
            ambient_r=value.get("ambient_r"),
            ambient_g=value.get("ambient_g"),
            ambient_b=value.get("ambient_b"),
            diffuse_r=value.get("diffuse_r"),
            diffuse_g=value.get("diffuse_g"),
            diffuse_b=value.get("diffuse_b"),
            specular_r=value.get("specular_r"),
            specular_g=value.get("specular_g"),
            specular_b=value.get("specular_b"),
            shininess=value.get("shininess"),
            roughness=value.get("roughness"),
            metallic=value.get("metallic"),
        )


def _initialize_models(
    rm: RendererManager, pw: PhysicsWorld, engine: Engine, models: dict
) -> None:
    for key, value in models.items():
        rm.new_model(
            name=key,
            mesh=value.get("mesh"),
            shader=value.get("shader"),
            texture=value.get("texture"),
            material=value.get("material"),
        )

        position = value.get("position")
        rotation = value.get("rotation")
        scale = value.get("scale")

        if position:
            rm.place(key, position.get("x"), position.get("y"), position.get("z"))

        if rotation:
            rm.rotate(key, rotation.get("x"), rotation.get("y"), rotation.get("z"))

        if scale:
            rm.scale(key, scale.get("x"), scale.get("y"), scale.get("z"))


def _initialize_physics(pw: PhysicsWorld, physics_bodies: dict) -> None:
    for key, value in physics_bodies.items():
        position = value.get("position")
        orientation = value.get("orientation")

        pw.new_body(
            key,
            shape=value.get("shape"),
            mass=value.get("mass"),
            position=(
                [position.get("x"), position.get("y"), position.get("z")]
                if position
                else [0, 0, 0]
            ),
            orientation=(
                [
                    orientation.get("x"),
                    orientation.get("y"),
                    orientation.get("z"),
                    orientation.get("w"),
                ]
                if orientation
                else [1, 0, 0, 0]
            ),
        )


def _initialize_links(engine: Engine, links: dict) -> None:
    for key, value in links.items():
        engine.create_link(key, value)
