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
