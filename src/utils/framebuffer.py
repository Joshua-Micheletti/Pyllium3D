"""Framebuffer utils."""

# ruff: noqa: F403, F405

from OpenGL.GL import *

from utils.messages import print_error


def check_framebuffer_status() -> None:
    """Check the framebuffer status and print the corresponding error."""
    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        error = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        print_error('Framebuffer error:')

        if error == GL_FRAMEBUFFER_UNDEFINED:
            print_error('GL_FRAMEBUFFER_UNDEFINED')
        if error == GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT:
            print_error('GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT')
        if error == GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT:
            print_error('GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT')
        if error == GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER:
            print_error('GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER')
        if error == GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER:
            print_error('GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER')
        if error == GL_FRAMEBUFFER_UNSUPPORTED:
            print_error('GL_FRAMEBUFFER_UNSUPPORTED')
        if error == GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE:
            print_error('GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE')
        if error == GL_FRAMEBUFFER_INCOMPLETE_LAYER_TARGETS:
            print_error('GL_FRAMEBUFFER_INCOMPLETE_LAYER_TARGETS')


def create_framebuffer(width: int, height: int) -> tuple[int, int, int]:
    """Create a framebuffer, color texture and depth texture."""
    framebuffer = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)

    color = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, color)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB32F, width, height, 0, GL_RGB, GL_FLOAT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    depth = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, depth)
    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_DEPTH_COMPONENT,
        width,
        height,
        0,
        GL_DEPTH_COMPONENT,
        GL_FLOAT,
        None,
    )
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, color, 0)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depth, 0)

    # check that the framebuffer was correctly initialized
    check_framebuffer_status()

    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    return (framebuffer, color, depth)


def create_multisample_framebuffer(width: int, height: int, samples: int) -> tuple[int, int, int]:
    """Create a multisample framebuffer.

    Args:
        width (int): Width of the framebuffer
        height (int): Height of the framebuffer
        samples (int): Number of samples of the framebuffer

    Returns:
        tuple[int, int, int]: Indices of the framebuffer, color texture and depth texture

    """
    # generate the framebuffer
    framebuffer = glGenFramebuffers(1)
    # bind it as the current framebuffer
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)

    # generate the texture to render the image to
    color = glGenTextures(1)
    # bind it to as the current texture
    glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, color)
    # generate the texture with the screen dimensions
    glTexImage2DMultisample(
        GL_TEXTURE_2D_MULTISAMPLE,
        samples,
        GL_RGB32F,
        width,
        height,
        GL_FALSE,
    )
    # glTexParameteri(GL_TEXTURE_2D_MULTISAMPLE, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    # glTexParameteri(GL_TEXTURE_2D_MULTISAMPLE, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    # glTexParameteri(GL_TEXTURE_2D_MULTISAMPLE, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    # glTexParameteri(GL_TEXTURE_2D_MULTISAMPLE, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    depth = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, depth)
    # glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.width, self.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
    glTexImage2DMultisample(
        GL_TEXTURE_2D_MULTISAMPLE,
        samples,
        GL_DEPTH_COMPONENT,
        width,
        height,
        GL_FALSE,
    )
    # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # bind the color texture and depth/stencil renderbuffer to the framebuffer
    # glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.color_render_texture, 0)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D_MULTISAMPLE, color, 0)
    # glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, self.depth_stencil_render_renderbuffer)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D_MULTISAMPLE, depth, 0)

    # check that the framebuffer was correctly initialized
    check_framebuffer_status()

    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    return (framebuffer, color, depth)


def create_cubemap_framebuffer(size: int = 512, mipmap: bool = False) -> tuple[int, int, int]:
    """Create a cubemap framebuffer.

    Args:
        size (int, optional): Size of the framebuffer (square). Defaults to 512.
        mipmap (bool, optional): If the cubemap framebuffer should support mipmaps or not. Defaults to False.

    Returns:
        tuple[int, int, int]: Indices of the framebuffer, color texture and renderbuffer of the cubemap

    """
    framebuffer = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)

    cubemap = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, cubemap)

    for i in range(6):
        glTexImage2D(
            GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
            0,
            GL_RGB,
            size,
            size,
            0,
            GL_RGB,
            GL_FLOAT,
            None,
        )

    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    if mipmap:
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glGenerateMipmap(GL_TEXTURE_CUBE_MAP)
    else:
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    renderbuffer = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, renderbuffer)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, size, size)

    # glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_CUBE_MAP_POSITIVE_X, cubemap, 0)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, renderbuffer)

    check_framebuffer_status()

    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    return (framebuffer, cubemap, renderbuffer)


def create_g_buffer(width: int, height: int) -> tuple[int, int, int, int, int, int]:
    """Create a GBuffer for deferred rendering.

    Args:
        width (int): Width of the GBuffer
        height (int): Height of the GBuffer

    Returns:
        tuple[int, int, int, int, int]: Framebuffer, position texture, normal texture, color texture, depth renderbuffer

    """
    g_buffer: int = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, g_buffer)

    # - position color buffer
    position_texture: int = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, position_texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB16F, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, position_texture, 0)

    # - normal color buffer
    normal_texture: int = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, normal_texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB16F, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, GL_TEXTURE_2D, normal_texture, 0)

    # - color + specular color buffer
    color_texture: int = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, color_texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB4, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT2, GL_TEXTURE_2D, color_texture, 0)

    # - metallic + roughness buffer
    pbr_texture: int = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, pbr_texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RG16F, width, height, 0, GL_RG, GL_UNSIGNED_BYTE, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT3, GL_TEXTURE_2D, pbr_texture, 0)

    # - tell OpenGL which color attachments we'll use (of this framebuffer) for rendering
    attachments: list[int] = [GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1, GL_COLOR_ATTACHMENT2, GL_COLOR_ATTACHMENT3]
    glDrawBuffers(4, attachments)

    depth_renderbuffer: int = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, depth_renderbuffer)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, width, height)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth_renderbuffer)

    check_framebuffer_status()

    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    return (g_buffer, position_texture, normal_texture, color_texture, pbr_texture, depth_renderbuffer)
