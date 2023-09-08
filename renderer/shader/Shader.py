from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GL import *

class Shader:
    def __init__(self, vert_path, frag_path):
        f = open(vert_path)
        vertex_src = f.read()

        f.close()

        f = open(frag_path)
        fragment_src = f.read()

        f.close()

        self.program = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        self.uniforms = dict()
        self._check_uniforms()
        

    def use(self):
        glUseProgram(self.program)

    def _check_uniforms(self):
        if glGetUniformLocation(self.program, "model") != -1:
            self.uniforms["model"] = glGetUniformLocation(self.program, "model")
        if glGetUniformLocation(self.program, "view") != -1:
            self.uniforms["view"] = glGetUniformLocation(self.program, "view")
        if glGetUniformLocation(self.program, "projection") != -1:
            self.uniforms["projection"] = glGetUniformLocation(self.program, "projection")


