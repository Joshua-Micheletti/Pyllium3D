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
        rm = RendererManager()

        # glBindFramebuffer(GL_FRAMEBUFFER, rm.render_framebuffer)
        self._render_scene()

        # glBindFramebuffer(GL_FRAMEBUFFER, 0)
        # self._render_screen()
        

    def _render_scene(self):
        # reset the timer
        self.timer.reset()

        # clear the framebuffer and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 

        # get a reference to the renderer manager
        rm = RendererManager()       
        
        # THIS LOOP WILL CHANGE WHEN THE MODELS WILL BE GROUPED BY SHADER, SO THAT THERE ISN'T SO MUCH CONTEXT SWITCHING
        # for every model in the renderer manager
        for name in rm.model_matrices:
            # if the model is the light model
            if name == "light":
                # render it using the white shader
                rm.shaders["white"].use()
                self._link_static_uniforms(rm.shaders["white"])
                self._link_dynamic_uniforms(rm.shaders["white"], name)
            else:
                rm.shaders["lighting"].use()
                self._link_static_uniforms(rm.shaders["lighting"])
                self._link_dynamic_uniforms(rm.shaders["lighting"], name)

            # bind the VAO of the current model
            glBindVertexArray(rm.vaos[name])
            # draw the mesh
            glDrawArrays(GL_TRIANGLES, 0, int(rm.vertices_count[name]))

        # record the time it took to render in the timer
        self.timer.record()

    # def _render_screen(self):


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
        
        
        
