"""Module to implement an object to do PBR deferred rendering."""

# ruff: noqa: F403, F405

import glm
from OpenGL.GL import *

from renderer.camera.camera import Camera
from renderer.material.material import Material
from renderer.model.model import Model
from renderer.shader.shader import Shader
from utils import create_g_buffer, get_ogl_matrix, get_query_time, Timer
from utils.framebuffer import create_framebuffer


class RasterDeferredRenderer:
    """Deferred Raster Renderer."""

    # ----------------------------------- Setup ---------------------------------- #
    def __init__(self, width: int = 800, height: int = 600) -> None:
        """Set the deferred renderer.

        Args:
            width (int, optional): Width of the renderer. Defaults to 800
            height (int, optional): Height of the renderer. Defaults to 600

        """
        # sizes of the renderer
        self._width: int = width
        self._height: int = height

        # rendering buffers
        self._g_buffer: int
        self._position_texture: int
        self._normal_texture: int
        self._color_texture: int
        self._pbr_texture: int
        self._depth_renderbuffer: int

        self._output_framebuffer: int
        self._output_texture: int
        self._output_depth: int

        # rendering shaders
        self._g_buffer_shader: Shader
        self._render_shader: Shader

        # track the rendering time
        self._ogl_timer: int = glGenQueries(1)[0]
        self._cpu_timer: Timer = Timer()

        self._setup_framebuffers()
        self._setup_shaders()

    def _setup_framebuffers(self) -> None:
        """Create the required framebuffers."""
        # create the gbuffer
        (
            self._g_buffer,
            self._position_texture,
            self._normal_texture,
            self._color_texture,
            self._pbr_texture,
            self._depth_renderbuffer,
        ) = create_g_buffer(self._width, self._height)

        # create the output rendering buffer
        self._output_framebuffer, self._output_texture, self._output_depth = create_framebuffer(
            self._width, self._height
        )

    def _setup_shaders(self) -> None:
        """Compile the required shaders."""
        # shader for creating the g buffer
        self._g_buffer_shader = Shader(
            './assets/shaders/deferred/g_buffer/g_buffer.vert', './assets/shaders/deferred/g_buffer/g_buffer.frag'
        )

        # shader for doing the lighting calculation
        self._render_shader = Shader(
            './assets/shaders/deferred/pbr_deferred/pbr_deferred.vert',
            './assets/shaders/deferred/pbr_deferred/pbr_deferred.frag',
        )

    # ---------------------------------- Getters --------------------------------- #
    @property
    def position_texture(self) -> int:
        """Texture storing the position data.

        Returns:
            int: Texture OpenGL ID

        """
        return self._position_texture

    @property
    def normal_texture(self) -> int:
        """Texture storing the normal data.

        Returns:
            int: Texture OpenGL ID

        """
        return self._normal_texture

    @property
    def color_texture(self) -> int:
        """Texture storing the color data.

        Returns:
            int: Texture OpenGL ID

        """
        return self._color_texture

    @property
    def pbr_texture(self) -> int:
        """Texture storing the PBR data.

        Returns:
            int: Texture OpenGL ID

        """
        return self._pbr_texture

    @property
    def depth_renderbuffer(self) -> int:
        """Renderbuffer storing the depth data.

        Returns:
            int: Renderbuffer OpenGL ID

        """
        return self._depth_renderbuffer

    @property
    def g_buffer(self) -> int:
        """Geometry Buffer storing the deferred rendering data.

        Returns:
            int: Buffer OpenGL ID

        """
        return self._g_buffer

    @property
    def ogl_timer(self) -> int:
        """Get the OpenGL query timer.

        Returns:
            int: OpenGL ID of the query object
            
        """
        return self._ogl_timer

    def get_rendering_time(self) -> float:
        """Get the elapsed rendering time from the renderer.

        Returns:
            float: Elapsed time in ms
        """
        return get_query_time(self._ogl_timer)

    def get_cpu_time(self) -> float:
        """Get the elapsed CPU time for rendering.

        Returns:
            float: CPU execution time in ms
            
        """
        self._cpu_timer.get_last_record()
        
    # ------------------------------ Public methods ------------------------------ #
    def render(
        self,
        models: dict[str, Model],
        vaos: dict[str, int],
        indices_counts: dict[str, int],
        materials: dict[str, Material],
        model_matrices: dict[str, any],
        projection_matrix: any,
        light: any,
        lights: any,
        light_colors: any,
        light_strengths: any,
        lights_count: any,
        far_plane: any,
        camera: Camera,
        bounding_sphere_centers: dict[str, glm.vec3],
        bounding_sphere_radiuses: dict[str, float],
        time: bool = False
    ) -> float:
        """Render in deferred rendering.

        Args:
            models (dict[str, Model]): Dictionary of models
            vaos (dict[str, int]): Dictionary of VAOs
            indices_counts (dict[str, int]): Dictionary of indices counts of meshes
            materials (dict[str, Material]): Dictionary of materials
            model_matrices (dict[str, any]): Dictionary of model matrices
            view_matrix (any): View matrix
            projection_matrix (any): Projection matrix
            eye (any): Position of the camera
            light (any): Position of the light casting shadow
            lights (any): List of light positions
            light_colors (any): List of light colors
            light_strengths (any): List of light strengths
            lights_count (any): Number of lights in the scene
            far_plane (any): Far plane of the shadow
            camera (Camera): Camera object
            bounding_sphere_centers (dict[str, glm.vec3]): Dictionary containing the center of all the bounding spheres
            bounding_sphere_radiuses: (dict[str, float]): Dictionary containing the radius of all the bounding spheres
            time (bool, optional): Optional parameter to keep track of the rendering time. Defaults to False.

        Returns:
            float: CPU Rendering time. 0 if time is set to False

        """
        # if the time flag is set to true, track the rendering time
        if time:
            self._cpu_timer.reset()
            glBeginQuery(GL_TIME_ELAPSED, self._ogl_timer)
            
        # bind the g buffer
        glBindFramebuffer(GL_FRAMEBUFFER, self._g_buffer)
        # clear its content
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # use the gbuffer shader
        self._g_buffer_shader.use()
        # setup the gbuffer shader uniforms
        self._g_buffer_shader.bind_uniform('view', camera.ogl_view_matrix)
        self._g_buffer_shader.bind_uniform('projection', get_ogl_matrix(projection_matrix))

        current_material_name: str = ''
        current_material: Material = None

        # iterate through the models in the scene
        for model in models:
            # check if the model is visible in the camera frustum
            if not camera.frustum.check_visibility(
                bounding_sphere_centers.get(model.name), bounding_sphere_radiuses.get(model.name)
            ):
                continue

            # if the model is using a new material, bind the necessary material parameters
            if model.material != current_material_name:
                current_material_name = model.material
                current_material = materials.get(current_material_name)
                self._g_buffer_shader.bind_uniform_float('albedo', current_material.diffuse)
                self._g_buffer_shader.bind_uniform_float('roughness', current_material.roughness)
                self._g_buffer_shader.bind_uniform_float('metallic', current_material.metallic)

            # bind the model information to be processed and saved in the gbuffer
            self._g_buffer_shader.bind_uniform('model', model_matrices.get(model.name))
            # bind the mesh VAO
            glBindVertexArray(vaos.get(model.mesh))
            # draw the element
            glDrawElements(GL_TRIANGLES, int(indices_counts.get(model.mesh)), GL_UNSIGNED_INT, None)

        # bind the output framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self._output_framebuffer)
        # clear its content
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # bind the screen quad VAO
        glBindVertexArray(vaos.get('screen_quad'))
        # use the PBR shader
        self._render_shader.use()
        # bind the necessary shader uniforms
        self._render_shader.bind_uniform('eye', camera.position)
        self._render_shader.bind_uniform('light', light)
        glUniform3fv(self._render_shader.uniforms.get('lights'), lights_count, lights)
        glUniform3fv(self._render_shader.uniforms.get('light_colors'), lights_count, light_colors)
        glUniform1fv(self._render_shader.uniforms.get('light_strengths'), lights_count, light_strengths)
        self._render_shader.bind_uniform_float('lights_count', lights_count)
        self._render_shader.bind_uniform('far_plane', far_plane)

        # assign texture slot 3 for the depth cubemap
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self._position_texture)
        # assign texture slot 4 for the irradiance cubemap
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self._normal_texture)
        # assign texture slot 5 for the reflection cubemap
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, self._color_texture)
        # assign texture slot 6 for the brdf integration texture
        glActiveTexture(GL_TEXTURE7)
        glBindTexture(GL_TEXTURE_2D, self._pbr_texture)

        # draw the screen quad
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        # blit the depth information from the gbuffer to the output framebuffer
        glBindFramebuffer(GL_READ_FRAMEBUFFER, self._g_buffer)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self._output_framebuffer)
        glBlitFramebuffer(
            0, 0, self._width, self._height, 0, 0, self._width, self._height, GL_DEPTH_BUFFER_BIT, GL_NEAREST
        )
        glBindFramebuffer(GL_FRAMEBUFFER, self._output_framebuffer)

        # if the time flag is set to true, stop the timing query
        if time:
            glEndQuery(GL_TIME_ELAPSED)
            return(self._cpu_timer.elapsed())
        
        return(0)

    def update_size(self, width: int, height: int) -> None:
        """Update the size of the renderer and rebuild the framebuffers and textures.

        Args:
            width (int): New width
            height (int): New height

        """
        # if the new dimensions are the same as the original ones, don't do anything
        if self._width == width and self._height == height:
            return

        # update the renderer sizes
        self._width = width
        self._height = height

        # recreate the framebuffers
        self._setup_framebuffers()
