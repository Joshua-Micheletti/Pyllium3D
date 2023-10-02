from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GL import *

# class to represent a shader object
class Shader:
    # constructor method, takes the path of the vertex and fragment shaders
    def __init__(self, vert_path, frag_path):
        # open the vertex shader file and store its content
        f = open(vert_path)
        vertex_src = f.read()
        f.close()

        # open the fragment shader file and store its content
        f = open(frag_path)
        fragment_src = f.read()
        f.close()

        # compile the OpenGL program from the vertex and fragment shaders
        self.program = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        # create a dictionary containing all the uniforms in the shader
        self.uniforms = dict()
        # check for uniforms in the shader
        self._check_uniforms()
        
    # function to use this program for rendering
    def use(self):
        glUseProgram(self.program)

    # function to check the presence of specific uniforms
    def _check_uniforms(self):
        # model matrix uniform (mat4)
        if glGetUniformLocation(self.program, "model") != -1:
            self.uniforms["model"] = glGetUniformLocation(self.program, "model")
        # view matrix uniform (mat4)
        if glGetUniformLocation(self.program, "view") != -1:
            self.uniforms["view"] = glGetUniformLocation(self.program, "view")
        # projection matrix uniform (mat4)
        if glGetUniformLocation(self.program, "projection") != -1:
            self.uniforms["projection"] = glGetUniformLocation(self.program, "projection")
        # light source position uniform (vec3)
        if glGetUniformLocation(self.program, "light") != -1:
            self.uniforms["light"] = glGetUniformLocation(self.program, "light")
        # camera position uniform (vec3)
        if glGetUniformLocation(self.program, "eye") != -1:
            self.uniforms["eye"] = glGetUniformLocation(self.program, "eye")
        # material ambient component
        if glGetUniformLocation(self.program, "ambient") != -1:
            self.uniforms["ambient"] = glGetUniformLocation(self.program, "ambient")
        # material diffuse component
        if glGetUniformLocation(self.program, "diffuse") != -1:
            self.uniforms["diffuse"] = glGetUniformLocation(self.program, "diffuse")
        # material specular component
        if glGetUniformLocation(self.program, "specular") != -1:
            self.uniforms["specular"] = glGetUniformLocation(self.program, "specular")
        # material shininess component
        if glGetUniformLocation(self.program, "shininess") != -1:
            self.uniforms["shininess"] = glGetUniformLocation(self.program, "shininess")
        # light ambient component
        if glGetUniformLocation(self.program, "light_ambient") != -1:
            self.uniforms["light_ambient"] = glGetUniformLocation(self.program, "light_ambient")
        # light diffuse component
        if glGetUniformLocation(self.program, "light_diffuse") != -1:
            self.uniforms["light_diffuse"] = glGetUniformLocation(self.program, "light_diffuse")
        # light specular component
        if glGetUniformLocation(self.program, "light_specular") != -1:
            self.uniforms["light_specular"] = glGetUniformLocation(self.program, "light_specular")

