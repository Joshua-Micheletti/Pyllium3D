"""Module to implement an object to do PBR deferred rendering."""

# ruff: noqa: F403, F405

from OpenGL.GL import *

from renderer.material.material import Material
from renderer.model.model import Model
from renderer.shader.shader import Shader
from utils import create_g_buffer, get_ogl_matrix
from utils.framebuffer import create_framebuffer


class RasterDeferredRenderer:
    """Deferred Raster Renderer."""
    
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
        self._pbr_shader = Shader(
            './assets/shaders/deferred/pbr_deferred/pbr_deferred.vert',
            './assets/shaders/deferred/pbr_deferred/pbr_deferred.frag',
        )

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

    def render(
        self,
        models: dict[str, Model],
        vaos: dict[str, int],
        indices_counts: dict[str, int],
        materials: dict[str, Material],
        model_matrices: dict[str, any],
        view_matrix: any,
        projection_matrix: any,
        eye: any,
        light: any,
        lights: any,
        light_colors: any,
        light_strengths: any,
        lights_count: any,
        far_plane: any,
    ) -> None:
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
            
        """
        # bind the g buffer
        glBindFramebuffer(GL_FRAMEBUFFER, self._g_buffer)
        # clear its content
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # use the gbuffer shader
        self._g_buffer_shader.use()
        # setup the gbuffer shader uniforms
        self._g_buffer_shader.bind_uniform('view', get_ogl_matrix(view_matrix))
        self._g_buffer_shader.bind_uniform('projection', get_ogl_matrix(projection_matrix))

        # iterate through the models in the scene
        for model in models:
            # bind the model information to be processed and saved in the gbuffer
            self._g_buffer_shader.bind_uniform_float('albedo', materials.get(model.material).diffuse)
            self._g_buffer_shader.bind_uniform_float('roughness', materials.get(model.material).roughness)
            self._g_buffer_shader.bind_uniform_float('metallic', materials.get(model.material).metallic)
            self._g_buffer_shader.bind_uniform('model', get_ogl_matrix(model_matrices.get(model.name)))
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
        self._pbr_shader.use()
        # bind the necessary shader uniforms
        self._pbr_shader.bind_uniform('eye', eye)
        self._pbr_shader.bind_uniform('light', light)
        glUniform3fv(self._pbr_shader.uniforms.get('lights'), lights_count, lights)
        glUniform3fv(self._pbr_shader.uniforms.get('light_colors'), lights_count, light_colors)
        glUniform1fv(self._pbr_shader.uniforms.get('light_strengths'), lights_count, light_strengths)
        self._pbr_shader.bind_uniform_float('lights_count', lights_count)
        self._pbr_shader.bind_uniform('far_plane', far_plane)

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
        glBlitFramebuffer(0, 0, self._width, self._height, 0, 0, self._width, self._height, GL_DEPTH_BUFFER_BIT, GL_NEAREST)
        glBindFramebuffer(GL_FRAMEBUFFER, self._output_framebuffer)
