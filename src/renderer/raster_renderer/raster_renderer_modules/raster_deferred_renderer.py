# ruff: noqa: F403, F405

from OpenGL.GL import *

from renderer.shader.shader import Shader
from utils import create_g_buffer, get_ogl_matrix
from utils.framebuffer import create_framebuffer


class RasterDeferredRenderer:
    def __init__(self, width: int, height: int) -> None:
        print('DEFERRED RENDERER')
        self._width: int = width
        self._height: int = height

        self._g_buffer: int
        self._position_texture: int
        self._normal_texture: int
        self._color_texture: int
        self._pbr_texture: int
        self._depth_renderbuffer: int
        self._g_buffer_shader: Shader

        self._setup_framebuffers()
        self._setup_shaders()

    def _setup_framebuffers(self) -> None:
        (
            self._g_buffer,
            self._position_texture,
            self._normal_texture,
            self._color_texture,
            self._pbr_texture,
            self._depth_renderbuffer,
        ) = create_g_buffer(self._width, self._height)

        self._output_framebuffer, self._output_texture, self._output_depth = create_framebuffer(
            self._width, self._height
        )

    def _setup_shaders(self) -> None:
        self._g_buffer_shader = Shader(
            './assets/shaders/deferred/g_buffer/g_buffer.vert', './assets/shaders/deferred/g_buffer/g_buffer.frag'
        )

        self._pbr_shader = Shader('./assets/shaders/deferred/pbr/pbr.vert', './assets/shaders/deferred/pbr/pbr.frag')

    def update_size(self, width: int, height: int) -> None:
        """Update the size of the renderer and rebuild the framebuffers and textures."""
        # if the new dimensions are the same as the original ones, don't do anything
        if self._width == width and self._height == height:
            return

        # update the renderer sizes
        self._width = width
        self._height = height

        self._setup_framebuffers()

    def render(
        self,
        models,
        vaos,
        indices_counts,
        materials,
        model_matrices,
        view_matrix: any,
        projection_matrix: any,
        eye,
        light,
        lights,
        light_colors,
        light_strengths,
        lights_count,
        far_plane,
    ) -> None:
        """Render in deferred rendering.

        Args:
            models (_type_): _description_
            vaos (_type_): _description_
            indices_counts (_type_): _description_
            model_matrices (_type_): _description_
            view_matrix (any): _description_
            projection_matrix (any): _description_

        """
        glBindFramebuffer(GL_FRAMEBUFFER, self._g_buffer)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._g_buffer_shader.use()
        self._g_buffer_shader.bind_uniform('view', get_ogl_matrix(view_matrix))
        self._g_buffer_shader.bind_uniform('projection', get_ogl_matrix(projection_matrix))

        for model in models:
            self._g_buffer_shader.bind_uniform_float('albedo', materials.get(model.material).diffuse)
            self._g_buffer_shader.bind_uniform_float('roughness', materials.get(model.material).roughness)
            self._g_buffer_shader.bind_uniform_float('metallic', materials.get(model.material).metallic)
            self._g_buffer_shader.bind_uniform('model', get_ogl_matrix(model_matrices.get(model.name)))
            glBindVertexArray(vaos.get(model.mesh))
            glDrawElements(GL_TRIANGLES, int(indices_counts.get(model.mesh)), GL_UNSIGNED_INT, None)

        glBindFramebuffer(GL_FRAMEBUFFER, self._output_framebuffer)
        glBindVertexArray(vaos.get('quad'))
        self._pbr_shader.use()
        self._pbr_shader.bind_uniform('eye', eye)
        self._pbr_shader.bind_uniform('light', light)
        # self._pbr_shader.bind_uniform('lights', lights, lights_count)
        # self._pbr_shader.bind_uniform('light_colors', light_colors, lights_count)
        # self._pbr_shader.bind_uniform('light_strengths', light_strengths, lights_count)
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

        glDrawElements(GL_TRIANGLES, int(indices_counts.get('quad')), GL_UNSIGNED_INT, None)
