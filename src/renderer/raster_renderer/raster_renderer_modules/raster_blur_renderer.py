# ruff: noqa: F403, F405

from OpenGL.GL import *

from renderer.shader.shader import Shader
from utils import create_framebuffer


class RasterBlurRenderer:
    """Render a blurred image."""
    
    def __init__(self, width: int, height: int, destination_framebuffer: int) -> None:
        """Set the initial parameters."""
        self._destination_framebuffer = destination_framebuffer
        
        self._width = 800
        self._height = 600

        self._horizontal_blur_shader: Shader = Shader(
            './assets/shaders/post_processing/horizontal_blur/horizontal_blur.vert',
            './assets/shaders/post_processing/horizontal_blur/horizontal_blur.frag',
        )

        self._vertical_blur_shader: Shader = Shader(
            './assets/shaders/post_processing/vertical_blur/vertical_blur.vert',
            './assets/shaders/post_processing/vertical_blur/vertical_blur.frag',
        )

        # framebuffer to render a blurred version of the normal render for depth of field effects
        self._blurred_framebuffer, self._blurred_texture, self._blurred_depth_texture = create_framebuffer(width, height)

    @property
    def destination_framebuffer(self) -> int:
        """Get and set the destination framebuffer."""
        return(self._destination_framebuffer)
    
    @destination_framebuffer.setter
    def destination_framebuffer(self, destination_framebuffer: int) -> None:
        self._destination_framebuffer = destination_framebuffer

    def update_size(self, width: int, height: int) -> None:
        """Update the size of the renderer and rebuild the framebuffers and textures."""
        self._width = width
        self._height = height
        self._blurred_framebuffer, self._blurred_texture, self._blurred_depth_texture = create_framebuffer(width, height)

    def render(self):
        """Render the scene with a gaussian blur."""
        # only render the blur texture if the depth of field or post processing effects are enabled
        # if not rm.render_states['depth_of_field'] and not rm.render_states['post_processing']:
        #     self.queries.get('blur')['active'] = False
        #     return ()

        # self.queries.get('blur')['active'] = True

        # if rm.render_states['profile']:
        #     glBeginQuery(GL_TIME_ELAPSED, self.queries.get('blur').get('ogl_id'))

        # bind the blurred framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self._destination_framebuffer)
        # clear the blur texture
        glClear(GL_COLOR_BUFFER_BIT)

        shader = rm.shaders['post_processing/horizontal_blur']
        self._horizontal_blur_shader.use()
        # glUniform1fv(shader.uniforms["gaussian_kernel"], 10, rm.gaussian_kernel_weights)
        glBindTexture(GL_TEXTURE_2D, rm.get_front_texture())
        glDrawElements(GL_TRIANGLES, rm.indices_count['screen_quad'], GL_UNSIGNED_INT, None)

        glBindFramebuffer(GL_FRAMEBUFFER, rm.blurred_framebuffer)
        glBindTexture(GL_TEXTURE_2D, rm.get_back_texture())
        shader = rm.shaders['post_processing/vertical_blur']
        shader.use()

        glDrawElements(GL_TRIANGLES, rm.indices_count['screen_quad'], GL_UNSIGNED_INT, None)

        if rm.render_states['profile']:
            glEndQuery(GL_TIME_ELAPSED)
