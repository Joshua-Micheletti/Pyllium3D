# ruff: noqa: F403, F405
from OpenGL.GL import *

from renderer.shader.shader import Shader
from utils import create_cubemap_framebuffer, create_projection_matrix, get_ogl_matrix


class RasterSkyboxRenderer:
    def __init__(self, width: int = 800, height: int = 600, resolution: int = 512, fov: int = 60) -> None:
        """Set the required parameters to render the skybox.

        Args:
            width (int, optional): Width of the renderer. Defaults to 800.
            height (int, optional): Height of the renderer. Defaults to 600.
            resolution (int, optional): Size of the skybox. Defaults to 512.
            fov (int, optional): Field of View of the renderer. Defaults to 60.

        """
        self._width = width
        self._height = height
        self._resolution = resolution
        self._fov = fov
        self._projection_matrix = get_ogl_matrix(create_projection_matrix(self._width, self._height))
        
        self._setup_shaders()
        self._setup_framebuffers()

    def _setup_shaders(self) -> None:
        # compile the skybox shader
        self._skybox_shader: Shader = Shader(
            './assets/shaders/skybox/skybox.vert',
            './assets/shaders/skybox/skybox.frag',
        )

    def _setup_framebuffers(self) -> None:
        self._output_framebuffer: int
        self._output_texture: int
        self._output_depth_texture: int

        self._output_framebuffer, self._output_texture, self._output_depth_texture = create_cubemap_framebuffer(
            self._resolution
        )

    @property
    def projection_matrix(self) -> None:
        """Get and set the projection matrix."""
        return self._projection_matrix

    @projection_matrix.setter
    def projection_matrix(self, projection_matrix: any) -> any:
        self._projection_matrix = projection_matrix

    @property
    def view_matrix(self) -> None:
        """Get and set the view matrix."""
        return self._view_matrix

    @view_matrix.setter
    def view_matrix(self, view_matrix: any) -> None:
        self._view_matrix = view_matrix

    def update_size(self, width: int, height: int) -> None:
        """Update the size of the renderer and rebuild the framebuffers and textures."""
        # if the new dimensions are the same as the original ones, don't do anything
        if self._width == width and self._height == height:
            return

        # update the renderer sizes
        self._width = width
        self._height = height

        # create the projection matrix
        self._projection_matrix = get_ogl_matrix(create_projection_matrix(self._width, self._height))
        # self._setup_framebuffers()

    def render(self) -> None:
        """Render the skybox."""
        # get a reference to the renderer manager

        # use the skybox shader
        self._skybox_shader.use()

        glUniformMatrix4fv(self._skybox_shader.uniforms['view'], 1, GL_FALSE, self._view_matrix)
        glUniformMatrix4fv(
            self._skybox_shader.uniforms['projection'],
            1,
            GL_FALSE,
            self._projection_matrix,
        )

        # disable cull facing
        glDisable(GL_CULL_FACE)
        # render the cube
        glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)
        # re-enable face culling
        glEnable(GL_CULL_FACE)
