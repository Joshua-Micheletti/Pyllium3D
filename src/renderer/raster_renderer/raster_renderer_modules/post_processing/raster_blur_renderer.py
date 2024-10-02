"""Module implementing the Raster Blur Renderer object."""

# ruff: noqa: F403, F405

from OpenGL.GL import *

from renderer.raster_renderer.raster_renderer_modules.post_processing.post_processing_renderer import (
    PostProcessingRenderer,
)
from renderer.shader.shader import Shader
from utils import create_framebuffer


class RasterBlurRenderer(PostProcessingRenderer):
    """Render a blurred image."""

    def _setup_framebuffers(self) -> None:
        super()._setup_framebuffers()
        # create the horizontal and vertical blur framebuffers and textures
        self._horizontal_blurred_framebuffer: int
        self._horizontal_blurred_texture: int
        self._horizontal_blurred_depth_texture: int

        (
            self._horizontal_blurred_framebuffer,
            self._horizontal_blurred_texture,
            self._horizontal_blurred_depth_texture,
        ) = create_framebuffer(self._width, self._height)

    def _setup_shaders(self) -> None:
        # compile the horizontal blur shader
        self._horizontal_blur_shader: Shader = Shader(
            './assets/shaders/post_processing/horizontal_blur/horizontal_blur.vert',
            './assets/shaders/post_processing/horizontal_blur/horizontal_blur.frag',
        )
        # compile the vertical blur shader
        self._vertical_blur_shader: Shader = Shader(
            './assets/shaders/post_processing/vertical_blur/vertical_blur.vert',
            './assets/shaders/post_processing/vertical_blur/vertical_blur.frag',
        )

    def render(self) -> None:
        """Render the scene with a 2 pass gaussian blur."""
        # --------- FIRST PASS (HORIZONTAL) ----------
        # bind the framebuffer to render the horizontally blurred image to
        glBindFramebuffer(GL_FRAMEBUFFER, self._horizontal_blurred_framebuffer)
        # clear the previous texture
        glClear(GL_COLOR_BUFFER_BIT)
        # use the horizontal blur shader
        self._horizontal_blur_shader.use()
        # bind the source texture as input, containing the image to blur
        glBindTexture(GL_TEXTURE_2D, self._source_texture)
        # render the horizontally blurred image
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        # --------- SECOND PASS (VERTICAL) ----------
        # bind the framebuffer to render the vertically blurred image to
        glBindFramebuffer(GL_FRAMEBUFFER, self._output_framebuffer)
        # use the vertical blur shader
        self._vertical_blur_shader.use()
        # bind the horizontally blurred image as input
        glBindTexture(GL_TEXTURE_2D, self._horizontal_blurred_texture)
        # render the vertically blurred image
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
