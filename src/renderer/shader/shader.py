from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GL import *

from utils import *

# class to represent a shader object
class Shader:
    # constructor method, takes the path of the vertex and fragment shaders
    @timeit()
    def __init__(self, vert_path, frag_path, geom_path = "") -> None:
        self.vertex_path = vert_path
        self.frag_path = frag_path
        self.geom_path = geom_path

        path_components = vert_path.split("/")

        self.name = path_components[-1].split(".")[0]
        # print_info(f"Compiling shader: {shader_name_components[0]}")

        # open the vertex shader file and store its content
        f = open(vert_path)
        vertex_src = f.read()
        f.close()

        # open the fragment shader file and store its content
        f = open(frag_path)
        fragment_src = f.read()
        f.close()

        geometry_src = ""

        if len(geom_path) != 0:
            f = open(geom_path)
            geometry_src = f.read()
            f.close()

        # compile the OpenGL program from the vertex and fragment shaders
        if len(geometry_src) != 0:
            self.program = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER), compileShader(geometry_src, GL_GEOMETRY_SHADER))
        else:
            self.program = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))

        # create a dictionary containing all the uniforms in the shader
        self.uniforms = dict()
        self.user_uniforms = dict()
        # check for uniforms in the shader
        self._check_uniforms()

        # print_success(f"Compiled shader:  {shader_name_components[0]}")
     
    def __str__(self) -> str:
        return(self.name)
    
    def __repr__(self) -> str:
        return("Shader obj")

    def compile(self):
        path_components = self.vertex_path.split("/")
        shader_name_components = path_components[-1].split(".")
        print_info(f"Compiling shader: {shader_name_components[0]}")

        f = open(self.vertex_path)
        vertex_src = f.read()
        f.close()

        # open the fragment shader file and store its content
        f = open(self.frag_path)
        fragment_src = f.read()
        f.close()

        geometry_src = ""

        if len(self.geom_path) != 0:
            f = open(self.geom_path)
            geometry_src = f.read()
            f.close()

        # compile the OpenGL program from the vertex and fragment shaders
        if len(geometry_src) != 0:
            self.program = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER), compileShader(geometry_src, GL_GEOMETRY_SHADER))
        else:
            self.program = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))

        # self.program = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))

        self.uniforms = dict()
        self.user_uniforms = dict()
        self._check_uniforms()

        print_success(f"Compiled shader:  {shader_name_components[0]}")

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

        if glGetUniformLocation(self.program, "skybox_view") != -1:
            self.uniforms["skybox_view"] = glGetUniformLocation(self.program, "skybox_view")

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

        if glGetUniformLocation(self.program, "time") != -1:
            self.uniforms["time"] = glGetUniformLocation(self.program, "time")

        if glGetUniformLocation(self.program, "screen_texture") != -1:
            self.uniforms["screen_texture"] = glGetUniformLocation(self.program, "screen_texture")

        if glGetUniformLocation(self.program, "blurred_texture") != -1:
            self.uniforms["blurred_texture"] = glGetUniformLocation(self.program, "blurred_texture")

        if glGetUniformLocation(self.program, "depth_texture") != -1:
            self.uniforms["depth_texture"] = glGetUniformLocation(self.program, "depth_texture")

        if glGetUniformLocation(self.program, "user_min") != -1:
            self.uniforms["user_min"] = glGetUniformLocation(self.program, "user_min")
            self.user_uniforms["user_min"] = 0
        if glGetUniformLocation(self.program, "user_max") != -1:
            self.uniforms["user_max"] = glGetUniformLocation(self.program, "user_max")
            self.user_uniforms["user_max"] = 0

        if glGetUniformLocation(self.program, "user_distance") != -1:
            self.uniforms["user_distance"] = glGetUniformLocation(self.program, "user_distance")
            self.user_uniforms["user_distance"] = 10
        if glGetUniformLocation(self.program, "user_range") != -1:
            self.uniforms["user_range"] = glGetUniformLocation(self.program, "user_range")
            self.user_uniforms["user_range"] = 5    

        if glGetUniformLocation(self.program, "user_parameter_0") != -1:
            self.uniforms["user_parameter_0"] = glGetUniformLocation(self.program, "user_parameter_0")
            self.user_uniforms["user_parameter_0"] = 1
        
        if glGetUniformLocation(self.program, "user_parameter_1") != -1:
            self.uniforms["user_parameter_1"] = glGetUniformLocation(self.program, "user_parameter_1")
            self.user_uniforms["user_parameter_1"] = 1

        if glGetUniformLocation(self.program, "user_parameter_2") != -1:
            self.uniforms["user_parameter_2"] = glGetUniformLocation(self.program, "user_parameter_2")
            self.user_uniforms["user_parameter_2"] = 1

        if glGetUniformLocation(self.program, "user_parameter_3") != -1:
            self.uniforms["user_parameter_3"] = glGetUniformLocation(self.program, "user_parameter_3")
            self.user_uniforms["user_parameter_3"] = 1

        if glGetUniformLocation(self.program, "samples") != -1:
            self.uniforms["samples"] = glGetUniformLocation(self.program, "samples")

        if glGetUniformLocation(self.program, "albedo") != -1:
            self.uniforms["albedo"] = glGetUniformLocation(self.program, "albedo")

        if glGetUniformLocation(self.program, "metallic") != -1:
            self.uniforms["metallic"] = glGetUniformLocation(self.program, "metallic")

        if glGetUniformLocation(self.program, "roughness") != -1:
            self.uniforms["roughness"] = glGetUniformLocation(self.program, "roughness")

        if glGetUniformLocation(self.program, "light_color") != -1:
            self.uniforms["light_color"] = glGetUniformLocation(self.program, "light_color")

        if glGetUniformLocation(self.program, "light_strength") != -1:
            self.uniforms["light_strength"] = glGetUniformLocation(self.program, "light_strength")

        if glGetUniformLocation(self.program, "lights") != -1:
            self.uniforms["lights"] = glGetUniformLocation(self.program, "lights")

        if glGetUniformLocation(self.program, "light_colors") != -1:
            self.uniforms["light_colors"] = glGetUniformLocation(self.program, "light_colors")

        if glGetUniformLocation(self.program, "light_strengths") != -1:
            self.uniforms["light_strengths"] = glGetUniformLocation(self.program, "light_strengths")

        if glGetUniformLocation(self.program, "lights_count") != -1:
            self.uniforms["lights_count"] = glGetUniformLocation(self.program, "lights_count")

        if glGetUniformLocation(self.program, "cube_matrices") != -1:
            self.uniforms["cube_matrices"] = glGetUniformLocation(self.program, "cube_matrices")

            for i in range(6):
                self.uniforms["cube_matrices[" + str(i) + "]"] = glGetUniformLocation(self.program, "cube_matrices[" + str(i) + "]")

        if glGetUniformLocation(self.program, "far_plane") != -1:
            self.uniforms["far_plane"] = glGetUniformLocation(self.program, "far_plane")

        if glGetUniformLocation(self.program, "depth_map") != -1:
            self.uniforms["depth_map"] = glGetUniformLocation(self.program, "depth_map")
        
        if glGetUniformLocation(self.program, "irradiance_map") != -1:
            self.uniforms["irradiance_map"] = glGetUniformLocation(self.program, "irradiance_map")

        if glGetUniformLocation(self.program, "reflection_map") != -1:
            self.uniforms["reflection_map"] = glGetUniformLocation(self.program, "reflection_map")

        if glGetUniformLocation(self.program, "brdf_integration") != -1:
            self.uniforms["brdf_integration"] = glGetUniformLocation(self.program, "brdf_integration")

        if glGetUniformLocation(self.program, "src_resolution") != -1:
            self.uniforms["src_resolution"] = glGetUniformLocation(self.program, "src_resolution")

        if glGetUniformLocation(self.program, "radius") != -1:
            self.uniforms["radius"] = glGetUniformLocation(self.program, "radius")

        if glGetUniformLocation(self.program, "gaussian_kernel") != -1:
            self.uniforms["gaussian_kernel"] = glGetUniformLocation(self.program, "gaussian_kernel")

        if glGetUniformLocation(self.program, "mip_level") != -1:
            self.uniforms["mip_level"] = glGetUniformLocation(self.program, "mip_level")