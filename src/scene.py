"""Set up the scene."""

from colorsys import hsv_to_rgb
from random import random

from engine.engine import Engine
from physics.physics_world import PhysicsWorld
from renderer.renderer_manager.renderer_manager import RendererManager
from utils import timeit
from utils.config import Config


@timeit()
def setup() -> None:
    """Set up the scene."""
    scene = Config().scene

    rm = RendererManager()
    pw = PhysicsWorld()
    engine = Engine()

    _initialize_meshes(rm, scene.get('meshes'))
    _initialize_textures(rm, scene.get('textures'))
    _initialize_materials(rm, scene.get('materials'))
    _initialize_models(rm, scene.get('models'))
    _initialize_physics(pw, scene.get('physics_bodies'))
    _initialize_links(engine, scene.get('links'))

    for i in range(2000):
        color = hsv_to_rgb(random(), 1, 1)
        rm.new_material(
            name=f'{i}_material',
            diffuse_r=color[0],
            diffuse_g=color[1],
            diffuse_b=color[2],
            roughness=random(),
            metallic=random(),
        )
        rm.new_model(f'{i}', 'sphere', 'pbr', None, f'{i}_material')
        rm.place(f'{i}', (random() - 0.5) * 40, (random() - 0.5) * 40 + 20, (random() - 0.5) * 40)


def update(dt: float) -> None:
    """Update the state of the entities.

    Args:
        dt (float): time that passed since the last update

    """
    rm = RendererManager()

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
    rm.place_light('sun', *rm.positions['sun'])
    # rm.place_light("light", *rm.positions["light"])
    # rm.place_light("moon", *rm.positions["moon"])


def _initialize_meshes(rm: RendererManager, meshes: dict) -> None:
    """Initialize all the meshes passed as an argument.

    Args:
    ----
    rm (RendererManager): RendererManager object reference
    meshes (dict): dictionary of paths to mesh files

    """
    for key, value in meshes.items():
        rm.mesh_manager.new_json_mesh(key, value)


def _initialize_textures(rm: RendererManager, textures: dict) -> None:
    rm.new_texture(
        'test',
        'assets/textures/uv-maptemplate.png',
    )


def _initialize_materials(rm: RendererManager, materials: dict) -> None:
    for key, value in materials.items():
        rm.new_material(
            key,
            ambient_r=value.get('ambient_r'),
            ambient_g=value.get('ambient_g'),
            ambient_b=value.get('ambient_b'),
            diffuse_r=value.get('diffuse_r'),
            diffuse_g=value.get('diffuse_g'),
            diffuse_b=value.get('diffuse_b'),
            specular_r=value.get('specular_r'),
            specular_g=value.get('specular_g'),
            specular_b=value.get('specular_b'),
            shininess=value.get('shininess'),
            roughness=value.get('roughness'),
            metallic=value.get('metallic'),
        )


def _initialize_models(rm: RendererManager, models: dict) -> None:
    for key, value in models.items():
        rm.new_model(
            name=key,
            mesh=value.get('mesh'),
            shader=value.get('shader'),
            texture=value.get('texture'),
            material=value.get('material'),
        )

        position = value.get('position')
        rotation = value.get('rotation')
        scale = value.get('scale')

        if position:
            rm.place(
                key,
                position.get('x'),
                position.get('y'),
                position.get('z'),
            )

        if rotation:
            rm.rotate(
                key,
                rotation.get('x'),
                rotation.get('y'),
                rotation.get('z'),
            )

        if scale:
            rm.scale(
                key,
                scale.get('x'),
                scale.get('y'),
                scale.get('z'),
            )


def _initialize_physics(pw: PhysicsWorld, physics_bodies: dict) -> None:
    for key, value in physics_bodies.items():
        position = value.get('position')
        orientation = value.get('orientation')

        pw.new_body(
            key,
            shape=value.get('shape'),
            mass=value.get('mass'),
            position=(
                [
                    position.get('x'),
                    position.get('y'),
                    position.get('z'),
                ]
                if position
                else [0, 0, 0]
            ),
            orientation=(
                [
                    orientation.get('x'),
                    orientation.get('y'),
                    orientation.get('z'),
                    orientation.get('w'),
                ]
                if orientation
                else [1, 0, 0, 0]
            ),
        )


def _initialize_links(engine: Engine, links: dict) -> None:
    for key, value in links.items():
        engine.create_link(key, value)
