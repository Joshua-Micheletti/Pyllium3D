"""Module implementing a post processing renderer."""

# ruff: noqa: F403, F405

from OpenGL.GL import *

from utils import create_framebuffer


class PostProcessingRenderer:
    """Render a blurred image."""

    def __init__(self, width: int = 800, height: int = 600, source_texture: int = 0) -> None:
        """Set the initial parameters of the renderer.

        Args:
            width (int, optional): Width of the renderer. Defaults to 800.
            height (int, optional): Height of the renderer. Defaults to 600.
            source_texture (int, optional): OpenGL texture to containing the starting frame. Defaults to 0.

        """
        self._width: int = width
        self._height: int = height
        self._source_texture: int = source_texture

        self._setup_framebuffers()
        self._setup_shaders()

    def _setup_framebuffers(self) -> None:
        self._output_framebuffer: int
        self._output_texture: int
        self._output_depth_texture: int

        self._output_framebuffer, self._output_texture, self._output_depth_texture = create_framebuffer(
            self._width, self._height
        )

    def _setup_shaders(self) -> None:
        pass

    @property
    def source_texture(self) -> int:
        """Get and set the source texture."""
        return self._source_texture

    @source_texture.setter
    def source_texture(self, source_texture: int) -> None:
        self._source_texture = source_texture

    @property
    def output_texture(self) -> int:
        """Get the output texture."""
        return self._output_texture

    @property
    def output_depth_texture(self) -> int:
        """Get the output depth texture."""
        return self._output_depth_texture

    def update_size(self, width: int, height: int) -> None:
        """Update the size of the renderer and rebuild the framebuffers and textures."""
        # if the new dimensions are the same as the original ones, don't do anything
        if self._width == width and self._height == height:
            return

        # update the renderer sizes
        self._width = width
        self._height = height

        self._setup_framebuffers()

    def render(self) -> None:
        """Render the effect."""
        pass
