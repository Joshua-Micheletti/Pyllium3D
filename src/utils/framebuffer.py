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
