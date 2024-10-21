"""Raster skybox renderer."""

# ruff: noqa: F403, F405
import numpy as np
from OpenGL.GL import *
from PIL import Image

from renderer.shader.shader import Shader
from utils import create_cubemap_framebuffer, create_projection_matrix, create_view_cubemap_matrices, get_ogl_matrix


class RasterSkyboxRenderer:
    """Class to render the skybox."""

    def __init__(
        self,
        path: str,
        width: int = 800,
        height: int = 600,
        skybox_size: int = 512,
        irradiance_size: int = 8,
        reflection_size: int = 128,
        fov: int = 60,
    ) -> None:
        """Set the required parameters to render the skybox.

        Args:
            path (str): Path to the skybox images
            width (int, optional): Width of the renderer. Defaults to 800.
            height (int, optional): Height of the renderer. Defaults to 600.
            skybox_size (int, optional): Size of the skybox. Defaults to 512.
            irradiance_size (int, optional): Size of the irradiance texture. Defaults to 32
            reflection_size (int, optional): Size of the reflection texture. Defaults to 128
            fov (int, optional): Field of View of the renderer. Defaults to 60.

        """
        # incoming arguments
        self._width: int = width
        self._height: int = height
        self._skybox_size: int = skybox_size
        self._irradiance_size: int = irradiance_size
        self._reflection_size: int = reflection_size
        self._fov: int = fov

        # matrices
        self._projection_matrix: any
        self._cubemap_projection_matrix: any
        self._center_cubemap_views: list[any]

        # textures
        self._equirect_skybox: int

        # shaders
        self._skybox_shader: Shader
        self._equirect_shader: Shader
        self._irradiance_shader: Shader
        self._reflection_shader: Shader

        # framebuffers
        self._skybox_framebuffer: int
        self._skybox_cubemap: int
        self._skybox_renderbuffer: int

        self._reflection_framebuffer: int
        self._reflection_cubemap: int
        self._reflection_renderbuffer: int

        self._irradiance_framebuffer: int
        self._irradiance_cubemap: int
        self._irradiance_renderbuffer: int

        self._ogl_timer: int = glGenQueries(1)[0]

        # setup
        self._setup_matrices()
        self._setup_shaders()
        self._setup_framebuffers()
        self._load_skybox(path)

    def _setup_matrices(self) -> None:
        """Set the required matrices for rendering the skybox."""
        self._projection_matrix = get_ogl_matrix(create_projection_matrix(self._width, self._height, self._fov))
        self._cubemap_projection_matrix = get_ogl_matrix(create_projection_matrix(1, 1, 90))
        self._center_cubemap_views = create_view_cubemap_matrices()

    def _setup_shaders(self) -> None:
        """Compile the shaders required for rendering the skybox."""
        self._skybox_shader = Shader(
            './assets/shaders/skybox/skybox.vert',
            './assets/shaders/skybox/skybox.frag',
        )
        # bind the already calculated projection matrix to the shader
        self._skybox_shader.use()
        self._skybox_shader.bind_uniform('projection', self._projection_matrix)

        self._equirect_shader = Shader(
            './assets/shaders/equirect_skybox/equirect_skybox.vert',
            './assets/shaders/equirect_skybox/equirect_skybox.frag',
        )

        self._irradiance_shader = Shader(
            './assets/shaders/irradiance_cube/irradiance_cube.vert',
            './assets/shaders/irradiance_cube/irradiance_cube.frag',
        )

        self._reflection_shader = Shader(
            './assets/shaders/reflection_prefilter/reflection_prefilter.vert',
            './assets/shaders/reflection_prefilter/reflection_prefilter.frag',
        )

    def _setup_framebuffers(self) -> None:
        """Create the required framebuffers, shaders and renderbuffers required for rendering the skybox."""
        self._skybox_framebuffer, self._skybox_cubemap, self._skybox_renderbuffer = create_cubemap_framebuffer(
            self._skybox_size
        )

        self._irradiance_framebuffer, self._irradiance_cubemap, self._irradiance_renderbuffer = (
            create_cubemap_framebuffer(self._irradiance_size)
        )

        self._reflection_framebuffer, self._reflection_cubemap, self._reflection_renderbuffer = (
            create_cubemap_framebuffer(self._reflection_size, mipmap=True)
        )

    def _load_skybox(self, filepath: str) -> None:
        # set the equirect skybox texture to None
        self._equirect_skybox = None

        # analize the path and detect if it's an equirect skybox or a cubemap
        components: list[str] = filepath.split('/')
        equirect: bool = '.' in components[-1]

        # if it's an equirect skybox
        if equirect:
            # create a 2d texture to hold the equirect image
            self._equirect_skybox = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self._equirect_skybox)

            # open the image and extract its data
            im = Image.open(filepath)
            im = im.convert('RGB')
            im = im.transpose(Image.FLIP_TOP_BOTTOM)
            imdata = np.fromstring(im.tobytes(), np.uint8)

            # store the pixel data into the OpenGL texture
            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
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

            # set the necessary texture parameters for the equirect 2d texture
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        else:
            # bind the skybox cubemap directly
            glBindTexture(GL_TEXTURE_CUBE_MAP, self._skybox_cubemap)

            # list of faces
            texture_faces: list[str] = []
            texture_faces.append(filepath + 'left.png')
            texture_faces.append(filepath + 'right.png')
            texture_faces.append(filepath + 'top.png')
            texture_faces.append(filepath + 'bottom.png')
            texture_faces.append(filepath + 'back.png')
            texture_faces.append(filepath + 'front.png')

            # iterate through the faces, load the image and store it in the right face of the cubemap
            for i in range(len(texture_faces)):
                # open the current image and get its pixel data
                im = Image.open(texture_faces[i])
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

        # bind the skybox cubemap
        glBindTexture(GL_TEXTURE_CUBE_MAP, self._skybox_cubemap)

        # set the texture behaviour
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        # method to render the skybox from an equirect to a cubemap
        self._render_equirectangular_skybox()
        # method to render the irradiance cubemap for light calculation
        self._render_irradiance_map()
        # method to render the reflection cubemap
        self._render_reflection_map()

    def _render_equirectangular_skybox(self) -> None:
        """Render the skybox from an equirectangular image to a cubemap."""
        # if there isn't an equirect skybox set, return immediately
        if self._equirect_skybox is None:
            return ()

        # set the viewport to the skybox dimensions
        glViewport(0, 0, self._skybox_size, self._skybox_size)
        # bind the skybox framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self._skybox_framebuffer)

        # use the equirect skybox shader
        self._equirect_shader.use()

        # set the projection uniform to the cubemap projection
        glUniformMatrix4fv(
            self._equirect_shader.uniforms.get('projection'),
            1,
            GL_FALSE,
            self._cubemap_projection_matrix,
        )

        # bind the source equirect skybox texture
        glBindTexture(GL_TEXTURE_2D, self._equirect_skybox)

        # disable backface culling
        glDisable(GL_CULL_FACE)

        # iterate through every face
        for i in range(6):
            # update the view matrix accordingly
            glUniformMatrix4fv(
                self._equirect_shader.uniforms.get('view'),
                1,
                GL_FALSE,
                get_ogl_matrix(self._center_cubemap_views[i]),
            )
            # bind the texture target of the framebuffer accordingly
            glFramebufferTexture2D(
                GL_FRAMEBUFFER,
                GL_COLOR_ATTACHMENT0,
                GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                self._skybox_cubemap,
                0,
            )
            # clear the previous texture
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # draw the face to the cubemap
            glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)

        # re-enable backface culling
        glEnable(GL_CULL_FACE)
        # set the viewport back to the render size
        glViewport(0, 0, self._width, self._height)

    def _render_irradiance_map(self) -> None:
        # set the viewport to the dimensions of the irradiance map size
        glViewport(0, 0, self._irradiance_size, self._irradiance_size)
        # bind the irradiance framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self._irradiance_framebuffer)

        # use the irradiance cubemap shader
        self._irradiance_shader.use()

        # bind the cubemap projection matrix to the projection uniform
        glUniformMatrix4fv(
            self._irradiance_shader.uniforms['projection'],
            1,
            GL_FALSE,
            self._cubemap_projection_matrix,
        )

        # bind the skybox texture cubemap as source
        glBindTexture(GL_TEXTURE_CUBE_MAP, self._skybox_cubemap)

        # disable face culling
        glDisable(GL_CULL_FACE)

        # iterate through all the faces of the cubemap
        for i in range(6):
            # update the view matrix
            glUniformMatrix4fv(
                self._irradiance_shader.uniforms['view'],
                1,
                GL_FALSE,
                get_ogl_matrix(self._center_cubemap_views[i]),
            )
            # update the framebuffer color attachment texture with the correct cubemap texture
            glFramebufferTexture2D(
                GL_FRAMEBUFFER,
                GL_COLOR_ATTACHMENT0,
                GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                self._irradiance_cubemap,
                0,
            )
            # clear the texture
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            # draw the irradiance texture
            glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)

        # re-enable backface culling
        glEnable(GL_CULL_FACE)

        # restore the viewport to the render dimensions
        glViewport(0, 0, self._width, self._height)

    def _render_reflection_map(self) -> None:
        # bind the reflection framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self._reflection_framebuffer)

        # use the reflection prefilter shader
        self._reflection_shader.use()

        # bind the projection matrix uniform to the cubemap projection matrix
        glUniformMatrix4fv(
            self._reflection_shader.uniforms['projection'],
            1,
            GL_FALSE,
            self._cubemap_projection_matrix,
        )

        # bind the skybox texture as source
        glBindTexture(GL_TEXTURE_CUBE_MAP, self._skybox_cubemap)

        # disable backface culling
        glDisable(GL_CULL_FACE)

        # set the max level of mipmaps
        max_mip_levels = 5

        # iterate through every mipmap level
        for mip in range(max_mip_levels):
            # calculate the resolution of the mipmap level
            mip_width = self._reflection_size * pow(0.5, mip)
            mip_height = self._reflection_size * pow(0.5, mip)

            # adapt the renderbuffer to accomodate the new resolution
            glBindRenderbuffer(GL_RENDERBUFFER, self._reflection_renderbuffer)
            glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, int(mip_width), int(mip_height))

            # set the viewport to the dimensions of the mipmap size
            glViewport(0, 0, int(mip_width), int(mip_height))

            # calculate the attributed roughness value
            roughness = float(mip) / float(max_mip_levels - 1)
            # bind the roughness uniform
            glUniform1f(self._reflection_shader.uniforms['roughness'], roughness)

            # iterate through every face of the cube
            for i in range(6):
                # update the view matrix for the correct face
                glUniformMatrix4fv(
                    self._reflection_shader.uniforms['view'],
                    1,
                    GL_FALSE,
                    get_ogl_matrix(self._center_cubemap_views[i]),
                )
                # bind the correct texture target in the framebuffer
                glFramebufferTexture2D(
                    GL_FRAMEBUFFER,
                    GL_COLOR_ATTACHMENT0,
                    GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                    self._reflection_cubemap,
                    mip,
                )
                # clear the framebuffer texture
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                # draw the blurred reflection map
                glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)

        # re-enable backface culling
        glEnable(GL_CULL_FACE)
        # set the viewport back to the renderer dimensions
        glViewport(0, 0, self._width, self._height)

    # ---------------------------- Getters and setters --------------------------- #
    @property
    def projection_matrix(self) -> any:
        """Get and set the projection matrix."""
        return self._projection_matrix

    @projection_matrix.setter
    def projection_matrix(self, projection_matrix: any) -> any:
        self._projection_matrix = projection_matrix

    @property
    def view_matrix(self) -> any:
        """Get and set the view matrix."""
        return self._view_matrix

    @view_matrix.setter
    def view_matrix(self, view_matrix: any) -> None:
        self._view_matrix = view_matrix

    @property
    def irradiance_cubemap(self) -> int:
        """Get the irradiance cubemap."""
        return self._irradiance_cubemap

    @property
    def reflection_cubemap(self) -> int:
        """Get the reflection cubemap."""
        return self._reflection_cubemap

    @property
    def ogl_timer(self) -> int:
        """OpenGL Query timer.

        Returns:
            int: OpenGL Query timer index

        """
        return self._ogl_timer

    # ------------------------------ Public methods ------------------------------ #
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

        # update the skybox uniform
        self._skybox_shader.use()
        self._skybox_shader.bind_uniform('projection', self._projection_matrix)

    def render(self, time: bool = False) -> None:
        """Render the skybox.

        Args:
            time (bool, optional): Flag whether to time the execution or not. Defaults to False.

        """
        if time:
            glBeginQuery(GL_TIME_ELAPSED, self._ogl_timer)

        # set the cubemap texture slot 0 with the skybox cubemap
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self._skybox_cubemap)

        # use the skybox shader
        self._skybox_shader.use()

        # pass the view matrix to the shader
        self._skybox_shader.bind_uniform('view', self._view_matrix)

        # disable cull facing
        glDisable(GL_CULL_FACE)
        # render the cube
        glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)
        # re-enable face culling
        glEnable(GL_CULL_FACE)

        if time:
            glEndQuery(GL_TIME_ELAPSED)
