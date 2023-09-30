from utils.Singleton import Singleton
from OpenGL.GL import *
import numpy as np
import glm

from utils.Timer import Timer
from renderer.RendererManager import RendererManager
from window.Window import Window

# class to render 3D models
class Renderer(metaclass=Singleton):
    # constructor method
    def __init__(self):
        # set the clear color to a dark grey
        glClearColor(0.1, 0.1, 0.1, 1.0)
        # enable depth testing (hide further away triangles if covered)
        glEnable(GL_DEPTH_TEST)
        # enable face culling (don't render the inside of triangles)
        glEnable(GL_CULL_FACE)
        # enable alpha blending (transparency)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # timer to keep track of the rendering time
        self.timer = Timer()

    # method to render the 3D models
    def render(self):
        # get a reference to the renderer manager
        rm = RendererManager()

        # bind the render framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, rm.render_framebuffer)
        # draw the scene to it
        self._render_scene()

        # bind the screen framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        # draw the render quad to it
        self._render_screen()
        

    def _render_scene(self):
        # reset the timer
        self.timer.reset()

        # clear the framebuffer and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 

        # get a reference to the renderer manager
        rm = RendererManager()

        # variables to keep track of the last used shader and mesh
        last_shader = ""
        last_mesh = ""
        
        # THIS LOOP WILL CHANGE WHEN THE MODELS WILL BE GROUPED BY SHADER, SO THAT THERE ISN'T SO MUCH CONTEXT SWITCHING
        # for every model in the renderer manager
        for name, model in rm.models.items():
            # check if the new model has a different shader
            if last_shader != model.shader:
                # if it has a different shader, change to the current shader
                rm.shaders[model.shader].use()
                # link the static uniforms (that don't change between meshes)
                self._link_static_uniforms(rm.shaders[model.shader])
                # keep track of the last set shader
                last_shader = model.shader

            # link the dynamic uniforms (that change from every model)
            self._link_dynamic_uniforms(rm.shaders[model.shader], name)

            # check if the new model has a different mesh
            if last_mesh != model.mesh:
                # if it does, bind the new VAO
                glBindVertexArray(rm.vaos[model.mesh])
                # and keep track of the last used mesh
                last_mesh = model.mesh

            # draw the mesh
            glDrawArrays(GL_TRIANGLES, 0, int(rm.vertices_count[model.mesh]))

        # record the time it took to render in the timer
        self.timer.record()

    def _render_screen(self):
        # get a reference to the renderer manager
        rm = RendererManager()

        # clear the color buffer
        glClear(GL_COLOR_BUFFER_BIT)
        # disable depth testing and cull face
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        
        # use the screen shader
        rm.shaders["screen"].use()
        # bind the screen quad VAO
        glBindVertexArray(rm.vaos["screen_quad"])
        # bind the render framebuffer color texture
        glBindTexture(GL_TEXTURE_2D, rm.color_render_texture)
        # draw the quad with the texture
        glDrawArrays(GL_TRIANGLES, 0, 6)

        # re-enable depth testing and cull face
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)


    # method to link static uniforms to the shader (static meaning they don't change between meshes)
    def _link_static_uniforms(self, shader):
        rm = RendererManager()
        if "view" in shader.uniforms:
            glUniformMatrix4fv(shader.uniforms["view"], 1, GL_FALSE, rm.camera.get_ogl_matrix())
        if "projection" in shader.uniforms:
            glUniformMatrix4fv(shader.uniforms["projection"], 1, GL_FALSE, Window().get_ogl_matrix())
        if "light" in shader.uniforms:
            glUniform3f(shader.uniforms["light"], rm.light_source.x, rm.light_source.y, rm.light_source.z)
        if "eye" in shader.uniforms:
            glUniform3f(shader.uniforms["eye"], rm.camera.position.x, rm.camera.position.y, rm.camera.position.z)

    # method to link dynamic uniforms to the shader (dynamic meaning they change between meshes)
    def _link_dynamic_uniforms(self, shader, name):
        rm = RendererManager()
        if "model" in shader.uniforms:
            glUniformMatrix4fv(shader.uniforms["model"], 1, GL_FALSE, rm.get_ogl_matrix(name))
        
        
        
