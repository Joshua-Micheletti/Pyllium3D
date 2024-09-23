"""Module implementing the Raster DOF Renderer object."""

# ruff: noqa: F403, F405

from OpenGL.GL import *

from renderer.raster_renderer.raster_renderer_modules import PostProcessingRenderer
from renderer.shader.shader import Shader


class RasterDOFRenderer(PostProcessingRenderer):
    """Render an image with Depth of Field."""

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        source_texture: int = 0,
        blur_texture: int = 0,
        depth_texture: int = 0,
    ) -> None:
        """Set the initial parameters of the renderer.

        Args:
            width (int, optional): Width of the renderer. Defaults to 800.
            height (int, optional): Height of the renderer. Defaults to 600.
            source_texture (int, optional): OpenGL texture to apply the effect to. Defaults to 0.
            blur_texture(int, optional): OpenGL texture of the blurred scene. Defaults to 0.
            depth_texture(int, optional): OpenGL texture of the depth of the scene. Defaults to 0.

        """
        self._blur_texture: int = blur_texture
        self._depth_texture: int = depth_texture
        super().__init__(width, height, source_texture)

    def _setup_shaders(self) -> None:
        # compile the depth of field shader
        self._depth_of_field_shader: Shader = Shader(
            './assets/shaders/depth_of_field/depth_of_field.vert',
            './assets/shaders/depth_of_field/depth_of_field.frag',
        )

    @property
    def blur_texture(self) -> int:
        """Get and set the blur texture."""
        return self._blur_texture

    @blur_texture.setter
    def blur_texture(self, blur_texture: int) -> None:
        self._blur_texture = blur_texture

    @property
    def depth_texture(self) -> int:
        """Get and set the depth texture."""
        return self._depth_texture

    @depth_texture.setter
    def depth_texture(self, depth_texture: int) -> None:
        self._depth_texture = depth_texture

    def render(self) -> None:
        """Render the scene."""
        # bind the main render framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self._output_framebuffer)
        # use the DOF shader
        self._depth_of_field_shader.use()

        glUniform1i(self._depth_of_field_shader.uniforms['screen_texture'], 0)
        glUniform1i(self._depth_of_field_shader.uniforms['blurred_texture'], 1)
        glUniform1i(self._depth_of_field_shader.uniforms['depth_texture'], 2)

        # bind the required textures to the correct texture slots
        glBindTexture(GL_TEXTURE_2D, self._source_texture)
        glActiveTexture(GL_TEXTURE0 + 1)
        glBindTexture(GL_TEXTURE_2D, self._blur_texture)
        glActiveTexture(GL_TEXTURE0 + 2)
        glBindTexture(GL_TEXTURE_2D, self._depth_texture)

        # draw the scene with depth of field
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        # set back the active texture slot to index 0
        glActiveTexture(GL_TEXTURE0)
