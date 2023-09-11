from utils.Singleton import Singleton
from OpenGL.GL import *
import numpy as np
import glm

from utils.Timer import Timer
from renderer.RendererManager import RendererManager
from window.Window import Window

class Renderer(metaclass=Singleton):
    def __init__(self):
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.timer = Timer()

    def render(self):
        self.timer.reset()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 

        rm = RendererManager()       
        
        for name in rm.model_matrices:
            if name == "light":
                rm.shaders["white"].use()
                self._link_static_uniforms(rm.shaders["white"])
                self._link_dynamic_uniforms(rm.shaders["white"], name)
            else:
                rm.shaders["lighting"].use()
                self._link_static_uniforms(rm.shaders["lighting"])
                self._link_dynamic_uniforms(rm.shaders["lighting"], name)

            
            glBindVertexArray(rm.vaos[name])
            glDrawArrays(GL_TRIANGLES, 0, int(rm.vertices_count[name]))

        self.timer.record()

    def _link_static_uniforms(self, shader):
        if "view" in shader.uniforms:
            glUniformMatrix4fv(shader.uniforms["view"], 1, GL_FALSE, RendererManager().camera.get_ogl_matrix())
        if "projection" in shader.uniforms:
            glUniformMatrix4fv(shader.uniforms["projection"], 1, GL_FALSE, Window().get_ogl_matrix())
        if "light" in shader.uniforms:
            light_source = RendererManager().light_source
            glUniform3f(shader.uniforms["light"], light_source.x, light_source.y, light_source.z)
        if "eye" in shader.uniforms:
            camera_position = RendererManager().camera.position
            glUniform3f(shader.uniforms["eye"], camera_position.x, camera_position.y, camera_position.z)

    def _link_dynamic_uniforms(self, shader, name):
        rm = RendererManager()
        if "model" in shader.uniforms:
            glUniformMatrix4fv(shader.uniforms["model"], 1, GL_FALSE, rm.get_ogl_matrix(name))
        
        
        
