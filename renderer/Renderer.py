from utils.singleton.Singleton import Singleton
from OpenGL.GL import *
import numpy as np
import glm

from renderer.RendererManager import RendererManager
from window.Window import Window

class Renderer(metaclass=Singleton):
    def __init__(self):
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_DEPTH_TEST)

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        shader = RendererManager().shaders["default"]
        shader.use()

        for name, model in RendererManager().models.items():
            self._link_uniforms(shader, model)
            # mvp = Window().projection_matrix * RendererManager().camera.view_matrix * model.model_matrix
            # mvp = Window().projection_matrix * RendererManager().camera.view_matrix * model.model_matrix
            # print(mvp)
            # glUniformMatrix4fv(glGetUniformLocation(shader.program, "mvp"), 1, GL_FALSE, glm.value_ptr(mvp))

            glBindBuffer(GL_ARRAY_BUFFER, model.vbo)

            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
            # glEnableVertexAttribArray(1)
            # glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

            glDrawArrays(GL_TRIANGLES, 0, int(model.vertices_count))

        
    def _link_uniforms(self, shader, model):
        if "model" in shader.uniforms:
            glUniformMatrix4fv(shader.uniforms["model"], 1, GL_FALSE, model.get_ogl_matrix())
        if "view" in shader.uniforms:
            glUniformMatrix4fv(shader.uniforms["view"], 1, GL_FALSE, RendererManager().camera.get_ogl_matrix())
        if "projection" in shader.uniforms:
            glUniformMatrix4fv(shader.uniforms["projection"], 1, GL_FALSE, Window().get_ogl_matrix())
        
        
