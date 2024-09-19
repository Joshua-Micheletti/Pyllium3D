"""Module to implement the Raster Bloom Renderer object."""

# ruff: noqa: F403, F405

from OpenGL.GL import *

from renderer.shader.shader import Shader
from utils import check_framebuffer_status


class RasterBloomRenderer:
    """Class to render the bloom effect. Takes a source texture to take the image from and a destination framebuffer to store the picture to."""

    def __init__(
        self, width: int, height: int, source_texture: int, destination_framebuffer: int, length: int = 5
    ) -> None:
        """Set the required parameters to render the bloom."""
        self._width: int = width
        self._height: int = height
        self._length: int = length

        self._source_texture: int = source_texture
        self._destination_framebuffer: int = destination_framebuffer

        self._downsample_shader: Shader = Shader(
            './assets/shaders/bloom_downsample/bloom_downsample.vert',
            './assets/shaders/bloom_downsample/bloom_downsample.frag',
        )

        self._upsample_shader: Shader = Shader(
            './assets/shaders/bloom_upsample/bloom_upsample.vert',
            './assets/shaders/bloom_upsample/bloom_upsample.frag',
        )

        self._bloom_shader: Shader = Shader(
            './assets/shaders/bloom/bloom.vert',
            './assets/shaders/bloom/bloom.frag',
        )

        self._setup_framebuffer()

    def _setup_framebuffer(self) -> None:
        # list of textures for the different mips levels
        self._bloom_mips: list[int] = []
        self._bloom_mips_sizes: list[tuple[int, int]] = []

        # create the framebuffer to render the bloom textures to
        self._framebuffer: int = glGenFramebuffers(1)
        # bind it as the main framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self._framebuffer)

        mip_size: tuple[int, int] = (int(self._width), int(self._height))

        # iterate through all the mips levels
        for i in range(self._length):
            # calculate the size of the mip texture
            mip_size: tuple[int, int] = (int(mip_size[0] / 2), int(mip_size[1] / 2))

            # add the current mip size to the list
            self._bloom_mips_sizes.append(mip_size)
            # add the current texture to the list
            self._bloom_mips.append(glGenTextures(1))

            # bind the current texture as the main texture
            glBindTexture(GL_TEXTURE_2D, self._bloom_mips[i])
            # create the texture
            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_R11F_G11F_B10F,
                mip_size[0],
                mip_size[1],
                0,
                GL_RGB,
                GL_FLOAT,
                None,
            )

            # set the texture parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        # assign the first mips texture to the framebuffer
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self._bloom_mips[0], 0)

        # check that the framebuffer is working as intended
        check_framebuffer_status()

        # bind back the screen framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def update_size(self, width: int, height: int) -> None:
        """Update the size of the bloom renderer."""
        if self._width != width or self._height != height:
            self._width = width
            self._height = height
            self._setup_framebuffer()

    @property
    def source_texture(self) -> int:
        """Get and set the source texture."""
        return self._source_texture

    @source_texture.setter
    def source_texture(self, source_texture: int) -> None:
        self._source_texture = source_texture

    @property
    def destination_framebuffer(self) -> int:
        """Get and set the destination framebuffer."""
        return self._destination_framebuffer

    @destination_framebuffer.setter
    def destination_framebuffer(self, destination_framebuffer: int) -> None:
        self._destination_framebuffer = destination_framebuffer

    def render(self) -> None:
        """Render the bloom effect."""
        # bind the internal framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self._framebuffer)

        # DOWNSAMPLE
        # bind the source texture containing the image to blur
        glBindTexture(GL_TEXTURE_2D, self._source_texture)

        # use the downsampling shader
        self._downsample_shader.use()
        # pass the resolution to the shader
        glUniform2f(self._downsample_shader.uniforms['src_resolution'], self._width, self._height)

        # iterate through all the mipmaps
        for i in range(len(self._bloom_mips)):
            # set the OpenGL viewport to the size of the mipmaps
            glViewport(0, 0, self._bloom_mips_sizes[i][0], self._bloom_mips_sizes[i][1])
            # bind the mipmap texture to the internal framebuffer
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self._bloom_mips[i], 0)
            # set the mipmap level in the shader
            glUniform1f(self._downsample_shader.uniforms['mip_level'], i)
            # draw the screen
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
            # pass the sizes of the mipmaps to the shader
            glUniform2f(
                self._downsample_shader.uniforms['src_resolution'],
                self._bloom_mips_sizes[i][0],
                self._bloom_mips_sizes[i][1],
            )
            # bind the current mipmap texture for the next pass
            glBindTexture(GL_TEXTURE_2D, self._bloom_mips[i])

        # UPSAMPLE
        # use the upsampling shader
        self._upsample_shader.use()

        # enable alpha blending
        glEnable(GL_BLEND)

        # iterate backwards through the mip levels
        for i in range(len(self._bloom_mips) - 1, 0, -1):
            # store the current and next mips
            current_mip = self._bloom_mips[i]
            next_mip = self._bloom_mips[i - 1]
            next_mip_size = self._bloom_mips_sizes[i - 1]

            # bind the current mip level texture
            glBindTexture(GL_TEXTURE_2D, current_mip)

            # change the OpenGL viewport with the size of the current mip texture
            glViewport(0, 0, next_mip_size[0], next_mip_size[1])
            # attach the mip texture to the framebuffer
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, next_mip, 0)

            # render the screen
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        # reset the viewport size
        glViewport(0, 0, self._width, self._height)

        # disable alpha blending
        glDisable(GL_BLEND)

        # BLENDING
        # bind the destination framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self._destination_framebuffer)
        # use the final bloom shader
        self._bloom_shader.use()

        # bind the initial texture on slot 0
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self._source_texture)
        # bind the result of the downsampling and upsampling to the texture on slot 1
        glActiveTexture(GL_TEXTURE0 + 1)
        glBindTexture(GL_TEXTURE_2D, self._bloom_mips[0])

        # draw the screen
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        # set the active texture back to texture slot 0
        glActiveTexture(GL_TEXTURE0)
