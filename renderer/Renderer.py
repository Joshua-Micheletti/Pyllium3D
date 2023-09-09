from utils.Singleton import Singleton
from OpenGL.GL import *
import numpy as np
import glm

from renderer.RendererManager import RendererManager
from window.Window import Window

class Renderer(metaclass=Singleton):
    def __init__(self):
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        rm = RendererManager()

        shader = rm.shaders["default"]
        shader.use()

        self._link_static_uniforms(shader)

        # for name, mesh in RendererManager().meshes.items():
        for name in rm.model_matrices:
            self._link_dynamic_uniforms(shader, name)

            glBindBuffer(GL_ARRAY_BUFFER, rm.vbos[name])

            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

            glDrawArrays(GL_TRIANGLES, 0, int(rm.vertices_count[name]))

    def _link_static_uniforms(self, shader):
        if "view" in shader.uniforms:
            glUniformMatrix4fv(shader.uniforms["view"], 1, GL_FALSE, RendererManager().camera.get_ogl_matrix())
        if "projection" in shader.uniforms:
            glUniformMatrix4fv(shader.uniforms["projection"], 1, GL_FALSE, Window().get_ogl_matrix())

    def _link_dynamic_uniforms(self, shader, name):
        rm = RendererManager()
        if "model" in shader.uniforms:
            glUniformMatrix4fv(shader.uniforms["model"], 1, GL_FALSE, rm.get_ogl_matrix(name))
        
        
        
