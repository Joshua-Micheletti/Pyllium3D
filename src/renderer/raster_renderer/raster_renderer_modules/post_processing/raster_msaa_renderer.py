"""Module implementing the Raster Blur Renderer object."""

# ruff: noqa: F403, F405

from OpenGL.GL import *

from renderer.raster_renderer.raster_renderer_modules.post_processing.post_processing_renderer import (
    PostProcessingRenderer,
)
from renderer.shader.shader import Shader


class RasterMSAARenderer(PostProcessingRenderer):
    """Render a blurred image."""

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        samples: int = 8,
        source_texture: int = 0,
        source_framebuffer: int = 0,
    ) -> None:
        """Set the MSAA anti aliasing renderer.

        Args:
            width (int, optional): Width of the renderer. Defaults to 800.
            height (int, optional): Height of the renderer. Defaults to 600.
            samples (int, optional): Number of samples. Defaults to 8.
            source_texture (int, optional): OpenGL source texture containing the image to AA. Defaults to 0.
            source_framebuffer (int, optional): OpenGL source framebuffer containing the depth texture to AA. Defaults to 0.

        """
        self._samples = samples
        self._source_framebuffer = source_framebuffer
        super().__init__(width, height, source_texture)

    def _setup_shaders(self) -> None:
        # compile the MSAA shader
        self._msaa_shader: Shader = Shader(
            './assets/shaders/msaa/msaa.vert',
            './assets/shaders/msaa/msaa.frag',
        )

        self._msaa_shader.use()
        self._msaa_shader.bind_uniform('samples', self._samples)

    @property
    def source_framebuffer(self) -> int:
        """Get and set the source framebuffer."""
        return self._source_framebuffer

    @source_framebuffer.setter
    def source_framebuffer(self, source_framebuffer: int) -> None:
        self._source_framebuffer = source_framebuffer

    @property
    def samples(self) -> int:
        """Get and set the number of samples."""
        return self._samples

    @samples.setter
    def samples(self, samples: int) -> None:
        self._samples = samples
        self._msaa_shader.use()
        self._msaa_shader.bind_uniform('samples', self._samples)

    def render(self, time: bool = False) -> None:
        """Render the scene MSAA antialiasing.

        Args:
            time (bool, optional): Flag whether to time the execution or not. Defaults to False.

        """
        if time:
            glBeginQuery(GL_TIME_ELAPSED, self._ogl_timer)

        # bind the solved framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self._output_framebuffer)
        # bind the multisample texture to resolve
        glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, self._source_texture)
        # use the msaa shader
        self._msaa_shader.use()
        # bind the samples uniform
        self._msaa_shader.bind_uniform('samples', self._samples)
        # render the MSAA texture
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        # resolve the depth buffer through nearest filtering
        glBindFramebuffer(GL_READ_FRAMEBUFFER, self._source_framebuffer)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self._output_framebuffer)
        glBlitFramebuffer(
            0,
            0,
            self._width,
            self._height,
            0,
            0,
            self._width,
            self._height,
            GL_DEPTH_BUFFER_BIT,
            GL_NEAREST,
        )

        if time:
            glEndQuery(GL_TIME_ELAPSED)
