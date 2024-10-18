# ruff: noqa: F403, F405

# main libraries imports
import os

import glm
import numpy as np
import OpenGL
import pyrr
from icecream import ic
from OpenGL.GL import *  # noqa: F403
from PIL import Image

from renderer.camera.camera import Camera
from renderer.material.material import Material
from renderer.renderer_manager.managers import MeshManager, instance_manager, light_manager, model_manager
from renderer.shader.shader import Shader

# custom modules imports
from utils import (
    Singleton,
    check_framebuffer_status,
    create_framebuffer,
    create_multisample_framebuffer,
    create_projection_matrix,
    print_error,
    timeit,
)

OpenGL.ERROR_CHECKING = False


# method to setup and handle all the required data for the renderer
class RendererManager(metaclass=Singleton):
    # --------------------------- Setup ---------------------------
    # constructor method
    @timeit()
    def __init__(self) -> None:
        """Method to initialize the RendererManager object."""
        # ============================= FIELDS SETUP =============================
        # ----------------------------- Rendering parameters -----------------------------
        # fields for screen dimensions
        self.width: int = 800
        self.height: int = 600

        # samples available for multisampling
        self.max_samples: int = glGetIntegerv(GL_MAX_COLOR_TEXTURE_SAMPLES)
        # selected sample count [0, self.max_samples]
        self.samples: int = self.max_samples

        # create the projection matrix for rendering
        self.fov: float = 60.0
        self.projection_matrix: glm.mat4 = create_projection_matrix(self.width, self.height, self.fov)

        # rendering states to modify the rendering pipeline
        self.render_states = {}
        self.render_states['depth_of_field'] = True
        self.render_states['post_processing'] = True
        self.render_states['shadow_map'] = True
        self.render_states['bloom'] = True
        self.render_states['profile'] = True

        self.irradiance_map_size = 32
        self.skybox_resolution = 512
        self.reflection_resolution = 64

        self.back_framebuffer = False

        # ----------------------------- Models -----------------------------
        # dictionary to keep track of model objects
        self.models = {}
        # dictionary to keep track of models that changed since the last update
        self.changed_models = {}
        # list of models to be rendered normally
        self.single_render_models = []

        # dictionary of model matrices
        self.model_matrices = {}
        self.ogl_model_matrices = {}

        # dictionary of trasformation factors of the meshes
        self.positions = {}
        self.rotations = {}
        self.scales = {}

        self.mesh_manager = MeshManager()

        # self.aabb_mins = {}
        # self.aabb_maxs = {}
        # self.bounding_sphere_radius = {}
        # self.bounding_sphere_center = {}
        self.model_bounding_sphere_center = {}
        self.model_bounding_sphere_radius = {}

        # # ----------------------------- Meshes -----------------------------
        # # dictionaries of OpenGL VBOs for vertex data (vertex, normal, uv)
        # self.vertex_vbos = {}
        # self.normal_vbos = {}
        # self.uv_vbos = {}
        # # dictionary of OpenGL EBOs for index data
        # self.ebos = {}
        # # dictionary of OpenGL VAO for vertex data
        # self.vaos = {}
        # # dictionary of number of vertices per mesh
        # self.vertices_count = {}
        # # dictionary of number of indices per mesh
        # self.indices_count = {}

        # ----------------------------- Shaders -----------------------------
        # dictionary of shaders compiled for the engine
        self.shaders = {}
        # list of post processing shaders active
        self.post_processing_shaders = []
        # list of available post processing shaders to apply
        self.available_post_processing_shaders = []

        # ----------------------------- Textures -----------------------------
        # dictionary of textures
        self.textures = {}

        self.equirect_skybox = None

        # ----------------------------- Materials -----------------------------
        # dictionary of material objects
        self.materials = {}

        # ----------------------------- Lights -----------------------------
        # dictionary to keep track of the light sources
        self.lights = {}
        # buffers for light colors, positions and strengths
        self.light_colors = []
        self.light_positions = []
        self.light_strengths = []
        # counter of lights in the scene
        self.lights_count = 0

        # ----------------------------- Shadows -----------------------------
        # size of the shadow depth texture
        self.shadow_size = 2048
        # far plane of the shadow
        self.shadow_far_plane = 100.0
        # projection matrix to render the shadowmap
        self.cubemap_projection = glm.perspective(glm.radians(90.0), 1.0, 0.1, self.shadow_far_plane)
        # list of transform matrices for shadow mapping
        self.shadow_transforms = []

        # ----------------------------- Instances -----------------------------
        # dictionary of instance objects
        self.instances = {}

        # ============================= METHODS SETUP =============================
        # method to setup shaders required for the rendering pipeline
        self._setup_shaders()
        # setup the required data for the engine
        self._setup_entities()
        # setup the rendering framebuffer
        self._setup_framebuffers()

        # self._expand_equirectangular_map_to_cubemap("assets/textures/alien/skybox.png")

    def __str__(self) -> str:
        return 'RendererManager'

    def __repr__(self) -> str:
        return 'RendererManager obj'

    # method to setup the shaders for the engine
    def _setup_shaders(self) -> None:
        # path of the shaders folder
        shaders_path = './assets/shaders/'

        # list of shader directories
        shader_directories = []
        # scroll through the filesystem and store the directories containing shaders
        for subdir, _, files in os.walk(shaders_path):
            if subdir != shaders_path and len(files) != 0:
                shader_directories.append(subdir)

        # scroll through the shader directories
        for shader_dir in shader_directories:
            # correct the directory path in case of "\" characters
            shader_dir = shader_dir.replace('\\\\', '/')
            shader_dir = shader_dir.replace('\\', '/')

            # extract the name of the shader from the directory
            name = shader_dir.replace(shaders_path, '')

            # extract the directories of the shader source files in the current shader directory
            sources = []
            for root, _, files in os.walk(shader_dir):
                for file in files:
                    sources.append(root + '/' + file)

            # variables to keep track of the shader components paths
            vert = ''
            frag = ''
            geom = ''

            # for each source file check what type it is
            for source in sources:
                extension = source.split('.')[-1]
                if extension == 'vert' or extension == 'vs':
                    vert = source
                elif extension == 'frag' or extension == 'fs':
                    frag = source
                elif extension == 'geom' or extension == 'gs':
                    geom = source

            # if there's a geometry shader, create the shader accordingly
            if vert != '' and frag != '' and geom != '':
                self.shaders[name] = Shader(vert, frag, geom)
            elif vert != '' and frag != '' and geom == '':
                self.shaders[name] = Shader(vert, frag)

            # if the shader name contains "post_processing", add it to the list of available post processing shaders
            if 'post_processing' in name:
                self.available_post_processing_shaders.append(name)

    # method to setup entities required for the rendering pipeline
    def _setup_entities(self) -> None:
        self.mesh_manager.new_json_mesh('screen_quad', 'assets/models/default/quad.json')
        self.mesh_manager.new_json_mesh('default', 'assets/models/default/box.json')

        self.new_material('default', *(0.2, 0.2, 0.2), *(0.6, 0.6, 0.6), *(1.0, 1.0, 1.0), 1.0)
        self.new_material('light_color', *(0.2, 0.2, 0.2), *(1.0, 1.0, 1.0), *(1.0, 1.0, 1.0), 1.0)

        self.new_texture('default', 'assets/textures/uv-maptemplate.jpg')

        # creation of a camera object
        self.camera = Camera()
        self.camera.frustum.aspect = float(self.width) / float(self.height)
        self.camera.frustum.fov_y = glm.radians(self.fov)
        self.camera.frustum.z_near = 0.1
        self.camera.frustum.z_far = 10000.0

        self.camera.place(0, 2, 5)
        # self.camera.turn(-90, -45)

        # creation of a light source object (just a position for now)
        self.new_light('sun', (0, 100, 0), (1, 1, 1), 30)
        self.new_light('main', light_strength=0)

        self.center_cubemap_views = []

        self.center_cubemap_views.append(glm.lookAt(glm.vec3(0.0), glm.vec3(1, 0, 0), glm.vec3(0, -1, 0)))
        self.center_cubemap_views.append(glm.lookAt(glm.vec3(0.0), glm.vec3(-1, 0, 0), glm.vec3(0, -1, 0)))
        self.center_cubemap_views.append(glm.lookAt(glm.vec3(0.0), glm.vec3(0, 1, 0), glm.vec3(0, 0, 1)))
        self.center_cubemap_views.append(glm.lookAt(glm.vec3(0.0), glm.vec3(0, -1, 0), glm.vec3(0, 0, -1)))
        self.center_cubemap_views.append(glm.lookAt(glm.vec3(0.0), glm.vec3(0, 0, 1), glm.vec3(0, -1, 0)))
        self.center_cubemap_views.append(glm.lookAt(glm.vec3(0.0), glm.vec3(0, 0, -1), glm.vec3(0, -1, 0)))

    # method for setting up the render framebuffer
    def _setup_framebuffers(self) -> None:
        # create the multisample framebuffer to do the main rendering of meshes
        self.render_framebuffer, self.multisample_render_texture, self.depth_texture = create_multisample_framebuffer(
            self.width, self.height, self.max_samples
        )
        # framebuffer to solve the multisample textures into a single sample texture through anti aliasing
        self.solved_framebuffer, self.solved_texture, self.solved_depth_texture = create_framebuffer(
            self.width, self.height
        )
        # temporary framebuffer to switch between for post processing
        self.tmp_framebuffer, self.tmp_texture, self.tmp_depth_texture = create_framebuffer(self.width, self.height)
        # depth only cubemap framebuffer for rendering a point light shadow map
        self.cubemap_shadow_framebuffer, self.depth_cubemap = self._create_depth_cubemap_framebuffer()

        (
            self.brdf_integration_framebuffer,
            self.brdf_integration_LUT,
            self.brdf_integration_depth,
        ) = create_framebuffer(width=512, height=512)

    # --------------------------- Creating Components ----------------------------------
    # method to create a new mesh, a count can be specified to generate more than 1 mesh with the same 3D model
    # @timeit(info_position=2, info=True)
    # def new_mesh(self, name: str, file_path: str) -> None:
    # """Method to create a new mesh from an obj file

    # Args:
    #     name (str): name of the new mesh
    #     file_path (str): directory of the .obj file

    # """
    # mesh_manager.new_mesh(self, name, file_path)

    # method to load json indiced meshes
    # @timeit()
    # def new_json_mesh(self, name: str, file_path: str) -> None:
    #     """Method to create a new mesh from a JSON file

    #     Args:
    #         name (str): name of the new mesh
    #         file_path (str): directory of the .json file

    #     """
    #     mesh_manager.new_json_mesh(self, name, file_path)

    # method to create a new shader
    def new_shader(self, name: str, vert_path: str, frag_path: str) -> None:
        self.shaders[name] = Shader(vert_path, frag_path)

    # method to create a new light
    def new_light(
        self,
        name: str,
        light_position: tuple[float, float, float] = (0.0, 0.0, 0.0),
        light_color: tuple[float, float, float] = (1.0, 1.0, 1.0),
        light_strength: float = 8.0,
    ) -> None:
        light_manager.new_light(self, name, light_position, light_color, light_strength)

    # method to generate a new texture (needs double checking if it's correct)
    def new_texture(self, name: str, filepath: str) -> None:
        # generate a new OpenGL texture
        self.textures[name] = glGenTextures(1)
        # bind the newly created texture
        glBindTexture(GL_TEXTURE_2D, self.textures[name])

        # setup the texture parameters
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        # load the texture image
        image = Image.open(filepath)
        # convert to RGBA
        convert = image.convert('RGBA')
        # flip the image and store the image into byte data
        image_data = convert.transpose(Image.FLIP_TOP_BOTTOM).tobytes()
        # store the size of the texture
        width = image.width
        height = image.height
        # close the image
        image.close()

        # bind the newly created texture
        glBindTexture(GL_TEXTURE_2D, self.textures[name])
        # store the data into the texture
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA8,
            width,
            height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            image_data,
        )

    # method to create a new material, composed of ambient, diffuse, specular colors and shininess value
    def new_material(
        self,
        name: str,
        ambient_r: float = 1.0,
        ambient_g: float = 1.0,
        ambient_b: float = 1.0,
        diffuse_r: float = 1.0,
        diffuse_g: float = 1.0,
        diffuse_b: float = 1.0,
        specular_r: float = 1.0,
        specular_g: float = 1.0,
        specular_b: float = 1.0,
        shininess: float = 1.0,
        roughness: float = 0.5,
        metallic: float = 0.5,
    ) -> None:
        if ambient_r is None:
            ambient_r = 1.0
        if ambient_g is None:
            ambient_g = 1.0
        if ambient_b is None:
            ambient_b = 1.0
        if diffuse_r is None:
            diffuse_r = 1.0
        if diffuse_g is None:
            diffuse_g = 1.0
        if diffuse_b is None:
            diffuse_b = 1.0
        if specular_r is None:
            specular_r = 1.0
        if specular_g is None:
            specular_g = 1.0
        if specular_b is None:
            specular_b = 1.0
        if shininess is None:
            shininess = 1.0
        if roughness is None:
            roughness = 0.5
        if metallic is None:
            metallic = 0.5

        self.materials[name] = Material(
            name,
            [ambient_r, ambient_g, ambient_b],
            [diffuse_r, diffuse_g, diffuse_b],
            [specular_r, specular_g, specular_b],
            shininess,
            roughness,
            metallic,
        )

    # method to create a new model
    def new_model(
        self,
        name: str,
        mesh: str = None,
        shader: str = None,
        texture: str = None,
        material: str = None,
        count: int = 1,
    ) -> None:
        model_manager.new_model(self, name, mesh, shader, texture, material, count)

    # method to create a new instance
    def new_instance(self, name: str, mesh: str = '', shader: str = '') -> None:
        """Method to create a new Instance

        Args:
            name (str): name of the new instance
            mesh (str, optional): name of the mesh to render the instance objects with. Defaults to "default".
            shader (str, optional): name of the shader to render the instance objects with. Defaults to "default".

        """
        instance_manager.new_instance(self, name, mesh, shader)

    # ---------------------------- Modify Instances -----------------------------------

    # method to add a model to an instance
    def add_model_to_instance(self, model: str, instance: str) -> None:
        """Method to add a model to an instance

        Args:
            model (str): name of the model to add to the instance
            instance (str): name of the instance to add the model to

        """
        instance_manager.add_model_to_instance(self, model, instance)

    def set_models_in_instance(self, models: list[str], instance_name: str) -> None:
        """Method to set all the models inside an instance

        Args:
            models (list[str]): list of model names to be the new list of models to render in the instance
            instance_name (str): name of the instance to modify

        """
        instance_manager.set_models_in_instance(self, models, instance_name)

    def remove_model_from_instance(self, model: str, instance: str) -> None:
        """Method to remove a model from an instance

        Args:
            model (str): name of the model to remove from the instance
            instance (str): name of the instance

        """
        instance_manager.remove_model_from_instance(self, model, instance)

    def set_instance_mesh(self, instance: str, mesh: str) -> None:
        """Method to set the mesh that the instance should render its objects with

        Args:
            instance (str): name of the instance
            mesh (str): name of the mesh

        """
        instance_manager.set_instance_mesh(self, instance, mesh)

    def set_instance_shader(self, instance: str, shader: str) -> None:
        """Method to set the shader that an instance should render its objects with

        Args:
            instance (str): name of the instance
            shader (str): name of the shader

        """
        instance_manager.set_instance_shader(self, instance, shader)

    def set_model_to_render_in_instance(self, model: str, instance: str) -> None:
        """Method to set a model to render inside an instance

        Args:
            model (str): name of the model to render
            instance (str): name of the instance

        """
        instance_manager.set_model_to_render_in_instance(self, model, instance)

    # method to initialize an instance, might move this inside the instance object
    def _initialize_instance(self, name: str) -> None:
        """Method to initialize an instance

        Args:
            name (str): name of the instance to initialize

        """
        instance_manager.initialize_instance(self, name)

    # ---------------------------- Modify Models -------------------------------------

    # method to place the mesh in a specific spot
    def place(self, name: str, x: float, y: float, z: float) -> None:
        model_manager.place(self, name, x, y, z)

    # method to move a mesh by a certain vector
    def move(self, name: str, x: float, y: float, z: float) -> None:
        model_manager.move(self, name, x, y, z)

    # method to rotate the mesh
    def rotate(self, name: str, x: float, y: float, z: float) -> None:
        model_manager.rotate(self, name, x, y, z)

    # method to scale the mesh
    def scale(self, name: str, x: float, y: float, z: float) -> None:
        model_manager.scale(self, name, x, y, z)

    def place_light(self, name: str, x: float, y: float, z: float) -> None:
        model_manager.place_light(self, name, x, y, z)

    # method to calculate the model matrix after a transformation
    def _calculate_model_matrix(self, name: str) -> None:
        model_manager.calculate_model_matrix(self, name)

    # method to check if an instance should be updated after a transformation
    def _check_instance_update(self, name: str) -> None:
        model_manager.check_instance_update(self, name)

    # ----------------------------- Modify Materials ---------------------------------

    def set_ambient(self, name: str, r: int, g: int, b: int) -> None:
        self.materials[name].set_ambient(r, g, b)
        self._check_instance_material_update(name, 'ambients')

    def set_diffuse(self, name: str, r: int, g: int, b: int) -> None:
        self.materials[name].set_diffuse(r, g, b)
        self._check_instance_material_update(name, 'diffuses')

    def set_specular(self, name: str, r: int, g: int, b: int) -> None:
        self.materials[name].set_specular(r, g, b)
        self._check_instance_material_update(name, 'speculars')

    def set_shininess(self, name: str, shininess: float) -> None:
        self.materials[name].set_shininess(shininess)
        self._check_instance_material_update(name, 'shininesses')

    def set_roughness(self, name: str, roughness: float) -> None:
        self.materials[name].set_roughness(roughness)
        self._check_instance_material_update(name, 'roughnesses')

    def set_metallic(self, name: str, metallicness: float) -> None:
        self.materials[name].set_metallic(metallicness)
        self._check_instance_material_update(name, 'metallicnesses')

    def set_light_color(self, name: str, r: int, g: int, b: int) -> None:
        if name in self.lights:
            self.light_colors[self.lights[name] * 3 + 0] = r
            self.light_colors[self.lights[name] * 3 + 1] = g
            self.light_colors[self.lights[name] * 3 + 2] = b
        else:
            print_error(f"Light '{name}' not found")

    def set_light_strength(self, name: str, strength: float) -> None:
        if name in self.lights:
            self.light_strengths[self.lights[name]] = strength
        else:
            print_error(f"Light '{name}' not found")

    def _check_instance_material_update(self, name: str, component: str) -> None:
        for model in self.materials[name].models:
            if model.in_instance != '':
                self.instances[model.in_instance].to_update[component] = True

                if component == 'ambients':
                    self.instances[model.in_instance].change_ambient(self.materials[name])
                if component == 'diffuses':
                    self.instances[model.in_instance].change_diffuse(self.materials[name])
                if component == 'speculars':
                    self.instances[model.in_instance].change_specular(self.materials[name])
                if component == 'shininesses':
                    self.instances[model.in_instance].change_shininess(self.materials[name])
                if component == 'roughnesses':
                    self.instances[model.in_instance].change_roughness(self.materials[name])
                if component == 'metallicnesses':
                    self.instances[model.in_instance].change_metallic(self.materials[name])

    # ---------------------------- Getters ------------------------------------------

    def light_material(self) -> Material:
        return self.materials['light_color']

    # method to obtain an OpenGL ready matrix
    def get_ogl_matrix(self, name: str) -> any:
        return glm.value_ptr(self.model_matrices[name])

    def get_ogl_projection_matrix(self) -> any:
        return glm.value_ptr(self.projection_matrix)

    def get_ogl_shadow_matrices(self) -> None:
        shadow_mats = []
        for i in range(len(self.shadow_transforms)):
            shadow_mats.append(glm.value_ptr(self.shadow_transforms[i]))

        return shadow_mats

    def get_ogl_inv_view_proj_matrix(self) -> 'pyrr.Matrix44':
        proj_view_matrix = self.projection_matrix * self.camera.view_matrix
        array = np.array(proj_view_matrix.to_list())

        inverted_proj_view_matrix = np.linalg.inv(array)

        glm_inverted_proj_view_matrix = glm.mat4(*inverted_proj_view_matrix.flatten())

        ic(glm_inverted_proj_view_matrix)

        # Extract the matrix data from glm.mat4
        glm_matrix_data = glm_inverted_proj_view_matrix.to_list()

        # Convert the list to a flat list (since glm.mat4.to_list() returns nested lists)
        flat_list = [item for sublist in glm_matrix_data for item in sublist]

        # Create a pyrr.Matrix4x4 object from the flat list
        pyrr_matrix = pyrr.Matrix44(flat_list)

        return pyrr_matrix

        # return glm.value_ptr(glm_inverted_proj_view_matrix)

    # ------------------------------ Updaters ---------------------------------------

    # method to update the dimensions of the screen
    def update_dimensions(self, width: int, height: int) -> None:
        # update the internal dimensions
        self.width = int(width)
        self.height = int(height)

        # self.projection_matrix = glm.perspective(
        #     glm.radians(self.fov), float(self.width) / float(self.height), 0.1, 10000.0
        # )
        self.projection_matrix = create_projection_matrix(self.width, self.height, self.fov)

        self.camera.frustum.aspect = float(self.width) / float(self.height)
        self.camera.frustum.fov_y = glm.radians(self.fov)
        self.camera.frustum.calculate_frustum()

        # delete the renderbuffer and the texture of the framebuffer
        glDeleteTextures(
            6,
            [
                self.multisample_render_texture,
                self.solved_texture,
                self.depth_texture,
                self.solved_depth_texture,
            ],
        )
        glDeleteFramebuffers(
            3,
            [
                self.render_framebuffer,
                self.solved_framebuffer,
            ],
        )

        self.render_framebuffer, self.multisample_render_texture, self.depth_texture = create_multisample_framebuffer(
            self.width, self.height, self.max_samples
        )
        self.solved_framebuffer, self.solved_texture, self.solved_depth_texture = create_framebuffer(
            self.width, self.height
        )
        self.tmp_framebuffer, self.tmp_texture, self.tmp_depth = create_framebuffer(self.width, self.height)

    # update method to update components of the rendering manager
    def update(self) -> None:
        for model in self.changed_models:
            self._calculate_model_matrix(model)
            self._check_instance_update(model)

            if model == 'sun':
                self.shadow_transforms = []
                sun_position = self.positions['sun']

                texel_size = 2.0 / self.shadow_size

                sun_position.x = round(sun_position.x / texel_size) * texel_size
                sun_position.y = round(sun_position.y / texel_size) * texel_size
                sun_position.z = round(sun_position.z / texel_size) * texel_size

                self.shadow_transforms.append(
                    self.cubemap_projection
                    * glm.lookAt(
                        sun_position,
                        sun_position + glm.vec3(1, 0, 0),
                        glm.vec3(0, -1, 0),
                    )
                )
                self.shadow_transforms.append(
                    self.cubemap_projection
                    * glm.lookAt(
                        sun_position,
                        sun_position + glm.vec3(-1, 0, 0),
                        glm.vec3(0, -1, 0),
                    )
                )
                self.shadow_transforms.append(
                    self.cubemap_projection
                    * glm.lookAt(
                        sun_position,
                        sun_position + glm.vec3(0, 1, 0),
                        glm.vec3(0, 0, 1),
                    )
                )
                self.shadow_transforms.append(
                    self.cubemap_projection
                    * glm.lookAt(
                        sun_position,
                        sun_position + glm.vec3(0, -1, 0),
                        glm.vec3(0, 0, -1),
                    )
                )
                self.shadow_transforms.append(
                    self.cubemap_projection
                    * glm.lookAt(
                        sun_position,
                        sun_position + glm.vec3(0, 0, 1),
                        glm.vec3(0, -1, 0),
                    )
                )
                self.shadow_transforms.append(
                    self.cubemap_projection
                    * glm.lookAt(
                        sun_position,
                        sun_position + glm.vec3(0, 0, -1),
                        glm.vec3(0, -1, 0),
                    )
                )

        self.changed_models = {}

    def update_instances(self) -> None:
        # update the instances
        for name, instance in self.instances.items():
            instance.previous_models_to_render = instance.models_to_render
            instance.models_to_render = {}

            for model in instance.models.values():
                if self.check_visibility(model.name):
                    self.set_model_to_render_in_instance(model.name, name)

            instance.update()

    def recompile_shaders(self) -> None:
        for _, shader in self.shaders.items():
            glDeleteProgram(shader.program)
            shader.compile()

    # ------------------------------ Misc --------------------------------------------

    def add_post_processing_shader(self, name: str) -> None:
        self.post_processing_shaders.append(self.shaders[name])

    def _create_depth_cubemap_framebuffer(self) -> tuple[int, int]:
        framebuffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)

        depth_cubemap = glGenTextures(1)

        glBindTexture(GL_TEXTURE_CUBE_MAP, depth_cubemap)

        for i in range(6):
            glTexImage2D(
                GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                0,
                GL_DEPTH_COMPONENT,
                self.shadow_size,
                self.shadow_size,
                0,
                GL_DEPTH_COMPONENT,
                GL_FLOAT,
                None,
            )

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_BORDER)

        border_color = [1.0, 1.0, 1.0, 1.0]
        border_color = np.array(border_color, dtype=np.float32)
        glTexParameterfv(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_BORDER_COLOR, border_color)

        glFramebufferTexture(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, depth_cubemap, 0)
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)

        # check that the framebuffer was correctly initialized
        check_framebuffer_status()

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        return (framebuffer, depth_cubemap)

    # glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    def get_front_framebuffer(self) -> int:
        return self.tmp_framebuffer if self.back_framebuffer else self.solved_framebuffer

    def get_back_framebuffer(self) -> int:
        return self.solved_framebuffer if self.back_framebuffer else self.tmp_framebuffer

    def get_back_texture(self) -> int:
        return self.solved_texture if self.back_framebuffer else self.tmp_texture

    def get_front_texture(self) -> int:
        return self.tmp_texture if self.back_framebuffer else self.solved_texture

    def swap_back_framebuffer(self) -> None:
        self.back_framebuffer = not self.back_framebuffer

    def set_samples(self, samples: int) -> None:
        if self.samples == samples:
            return ()

        self.samples = samples

    # method for doing frustum culling
    def check_visibility(self, model: str) -> bool:
        # get the model's bounding sphere's center and radius
        center = self.model_bounding_sphere_center[model]
        radius = self.model_bounding_sphere_radius[model]

        # return(True)

        if not self.is_on_forward_plane(self.camera.frustum.near, center, radius):
            return False
        if not self.is_on_forward_plane(self.camera.frustum.bottom, center, radius):
            return False
        if not self.is_on_forward_plane(self.camera.frustum.far, center, radius):
            return False
        if not self.is_on_forward_plane(self.camera.frustum.left, center, radius):
            return False
        if not self.is_on_forward_plane(self.camera.frustum.right, center, radius):
            return False
        if not self.is_on_forward_plane(self.camera.frustum.top, center, radius):  # noqa: SIM103
            return False

        return True

    def is_on_forward_plane(self, plane: any, center: any, radius: float) -> any:
        return glm.dot(plane.normal, center) - plane.distance > -radius
