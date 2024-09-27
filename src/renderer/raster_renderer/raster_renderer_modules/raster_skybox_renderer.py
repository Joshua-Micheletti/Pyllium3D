# ruff: noqa: F403, F405
import glm
import numpy as np
from OpenGL.GL import *
from PIL import Image

from renderer.shader.shader import Shader
from utils import create_cubemap_framebuffer, create_projection_matrix, get_ogl_matrix


class RasterSkyboxRenderer:
    """Class to render the skybox."""

    def __init__(self, path: str, width: int = 800, height: int = 600, resolution: int = 512, fov: int = 60) -> None:
        """Set the required parameters to render the skybox.

        Args:
            path (str): Path to the skybox images
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
        self._cubemap_projection_matrix = get_ogl_matrix(create_projection_matrix(1, 1, 90))

        self._equirect_skybox = None

        self._setup_shaders()
        self._setup_framebuffers()
        self._load_skybox(path)

    def _setup_shaders(self) -> None:
        # compile the skybox shader
        self._skybox_shader: Shader = Shader(
            './assets/shaders/skybox/skybox.vert',
            './assets/shaders/skybox/skybox.frag',
        )

        self._equirect_shader: Shader = Shader(
            './assets/shaders/equirect_skybox/equirect_skybox.vert',
            './assets/shaders/equirect_skybox/equirect_skybox.frag',
        )

        self._irradiance_shader: Shader = Shader(
            './assets/shaders/irradiance_cube/irradiance_cube.vert',
            './assets/shaders/irradiance_cube/irradiance_cube.frag',
        )

    def _setup_framebuffers(self) -> None:
        self._skybox_framebuffer: int
        self._skybox_cubemap: int
        self._skybox_renderbuffer: int

        self._skybox_framebuffer, self._skybox_cubemap, self._skybox_renderbuffer = create_cubemap_framebuffer(
            self._resolution
        )

        self._irradiance_framebuffer: int
        self._irradiance_cubemap: int
        self._irradiance_renderbuffer: int

        self.irradiance_framebuffer, self.irradiance_cubemap, self.irradiance_renderbuffer = create_cubemap_framebuffer(
            self.irradiance_map_size
        )

        self._reflection_framebuffer: int
        self._reflection_cubemap: int
        self._reflection_renderbuffer: int

        self._reflection_framebuffer, self._reflection_cubemap, self._reflection_renderbuffer = (
            create_cubemap_framebuffer(self.reflection_resolution, mipmap=True)
        )

    def _load_skybox(self, filepath: str) -> None:
        components = filepath.split('/')

        equirect = '.' in components[-1]

        if equirect:
            self.equirect_skybox = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.equirect_skybox)

            im = Image.open(filepath)  # .transpose(Image.FLIP_TOP_BOTTOM)
            im = im.convert('RGB')
            im = im.transpose(Image.FLIP_TOP_BOTTOM)
            # get the data of the loaded face image
            imdata = np.fromstring(im.tobytes(), np.uint8)

            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
            # store the data of the image in the cubemap texture
            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RGB,
                im.size[0],
                im.size[1],
                0,
                GL_RGB,
                GL_UNSIGNED_BYTE,
                imdata,
            )

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

            glBindTexture(GL_TEXTURE_CUBE_MAP, self.skybox_texture)

            # generate a cubemap texture
            # self.skybox_texture = glGenTextures(1)
            # glBindTexture(GL_TEXTURE_CUBE_MAP, self.skybox_texture)
            # for i in range(6):
            #     glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB, self.skybox_resolution, self.skybox_resolution, 0, GL_RGB, GL_UNSIGNED_BYTE, None)

        else:
            # generate a cubemap texture
            # self.skybox_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_CUBE_MAP, self.skybox_texture)

            # list of faces
            texture_faces = []
            texture_faces.append(filepath + 'left.png')
            texture_faces.append(filepath + 'right.png')
            texture_faces.append(filepath + 'top.png')
            texture_faces.append(filepath + 'bottom.png')
            texture_faces.append(filepath + 'back.png')
            texture_faces.append(filepath + 'front.png')

            # iterate through the faces, load the image and store it in the right face of the cubemap
            for i in range(len(texture_faces)):
                im = Image.open(texture_faces[i])  # .transpose(Image.FLIP_TOP_BOTTOM)
                im = im.convert('RGB')

                # get the data of the loaded face image
                imdata = np.fromstring(im.tobytes(), np.uint8)

                # store the data of the image in the cubemap texture
                glTexImage2D(
                    GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                    0,
                    GL_RGB,
                    im.size[0],
                    im.size[1],
                    0,
                    GL_RGB,
                    GL_UNSIGNED_BYTE,
                    imdata,
                )

        # set the texture behaviour
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        # # load the skybox rendering shader
        # self.shaders["skybox"] = Shader("assets/shaders/skybox/skybox.vert", "assets/shaders/skybox/skybox.frag")

        # method to render the skybox from an equirect to a cubemap
        self._render_equirectangular_skybox()
        # method to render the irradiance cubemap for light calculation
        self._render_irradiance_map()
        # method to render the reflection cubemap
        self._render_reflection_map()

    def _render_equirectangular_skybox(self) -> None:
        # reference to the renderer manager

        # if there isn't an equirect skybox set, return immediately
        if self._equirect_skybox is None:
            return ()

        # set the viewport to the skybox dimensions
        glViewport(0, 0, self._resolution, self._resolution)
        # bind the skybox framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self._skybox_framebuffer)

        # use the equirect skybox shader
        self._equirect_shader.use()

        # set the projection uniform to the cubemap projection
        glUniformMatrix4fv(
            self._equirect_shader.uniforms['projection'],
            1,
            GL_FALSE,
            glm.value_ptr(self._cubemap_projection_matrix),
        )

        # bind the cube mesh VAO
        # glBindVertexArray(rm.vaos['default'])

        # bind the source equirect skybox texture
        glBindTexture(GL_TEXTURE_2D, self._equirect_skybox)

        # disable backface culling
        glDisable(GL_CULL_FACE)

        # iterate through every face
        for i in range(6):
            # update the view matrix accordingly
            glUniformMatrix4fv(
                self._equirect_shader.uniforms['view'],
                1,
                GL_FALSE,
                glm.value_ptr(rm.center_cubemap_views[i]),
            )
            # bind the texture target of the framebuffer accordingly
            glFramebufferTexture2D(
                GL_FRAMEBUFFER,
                GL_COLOR_ATTACHMENT0,
                GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                rm.skybox_texture,
                0,
            )
            # clear the previous texture
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # draw the face to the cubemap
            glDrawElements(GL_TRIANGLES, rm.indices_count['default'], GL_UNSIGNED_INT, None)

        # re-enable backface culling
        glEnable(GL_CULL_FACE)
        # set the viewport back to the render size
        glViewport(0, 0, self._width, self._height)

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
        """Update the size of the renderer and rebuild the framebuffers and textures.

        Args:
            width (int): New width of the renderer
            height (int): New height of the renderer

        """
        # if the new dimensions are the same as the original ones, don't do anything
        if self._width == width and self._height == height:
            return

        # update the renderer sizes
        self._width = width
        self._height = height

        # create the projection matrix
        self._projection_matrix = get_ogl_matrix(create_projection_matrix(self._width, self._height))

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
