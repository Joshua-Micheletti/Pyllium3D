from OpenGL.GL import *
import numpy as np
import pywavefront
import glm

from utils.Singleton import Singleton
from renderer.model.Mesh import Model
from renderer.shader.Shader import Shader
from renderer.camera.Camera import Camera

# method to setup and handle all the required data for the renderer
class RendererManager(metaclass=Singleton):
    # constructor method
    def __init__(self):
        # UNUSED
        self.meshes = dict()

        # dictionaries of OpenGL VBOs for vertex data (vertex, normal, uv)
        self.vertex_vbos = dict()
        self.normal_vbos = dict()
        self.uv_vbos = dict()
        # dictionary of OpenGL VAO for vertex data
        self.vaos = dict()

        # dictionary of model matrices
        self.model_matrices = dict()
        # dictionary of number of vertices per mesh
        self.vertices_count = dict()
        # dictionary of trasformation factors of the meshes
        self.positions = dict()
        self.rotations = dict()
        self.scales = dict()

        # dictionary of shaders compiled for the engine
        self.shaders = dict()

        # setup the required data for the engine
        self._setup_entities()

        self._setup_render_framebuffer()
        
    # method to setup the required entities for the engine
    def _setup_entities(self):
        # compilation of necessary shaders for the engine
        self.shaders["lighting"] = Shader("./shaders/lighting/lighting.vert", "./shaders/lighting/lighting.frag")
        self.shaders["white"] = Shader("./shaders/white/white.vert", "./shaders/white/white.frag")
        
        # creation of a camera object
        self.camera = Camera()

        # creation of a light source object (just a position for now)
        self.light_source = glm.vec3(10, 10, 10)

    def _setup_render_framebuffer(self):
        self.render_framebuffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.render_framebuffer)
        

        

        self.color_render_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.color_render_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 800, 600, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        self.depth_stencil_render_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depth_stencil_render_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_STENCIL, 800, 600, 0, GL_DEPTH24_STENCIL8, GL_UNSIGNED_BYTE, None)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.color_render_texture, 0)
        # glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_TEXTURE_2D, self.depth_stencil_render_texture, 0);  
        
        
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE:
            print("framebuffer initialized correctly")
        else:
            print("framebuffer error")


        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # method to create a new mesh, a count can be specified to generate more than 1 mesh with the same 3D model
    def new_mesh(self, name, file_path, count = 1):
        # empty lists to contain the vertices data taken from the file
        formatted_vertices = []
        formatted_normals = []
        formatted_uvs = []

        # load the mesh from the file path
        scene = pywavefront.Wavefront(file_path, collect_faces = True)

        # iterate through all the meshes in the file
        for key, material in scene.materials.items():
            # scroll through the vertices data by increments of 8 (u, v, n.x, n.y, n.z, v.x, v.y, v.z)
            for i in range(0, len(material.vertices), 8):
                # u
                formatted_uvs.append(material.vertices[i])
                # v
                formatted_uvs.append(material.vertices[i+1])

                # n.x
                formatted_normals.append(material.vertices[i+2])
                # n.y
                formatted_normals.append(material.vertices[i+3])
                # n.z
                formatted_normals.append(material.vertices[i+4])

                # v.x
                formatted_vertices.append(material.vertices[i+5])
                # v.y
                formatted_vertices.append(material.vertices[i+6])  
                # v.z              
                formatted_vertices.append(material.vertices[i+7])

        # format the lists into np.arrays of type float 32
        formatted_vertices = np.array(formatted_vertices, dtype=np.float32)
        formatted_normals = np.array(formatted_normals, dtype=np.float32)
        formatted_uvs = np.array(formatted_uvs, dtype=np.float32)

        # store the original name to create multiple names out of it, in case the parameter "count" is set
        original_name = name

        # iterate "count" times (1 by default)
        for i in range(count):
            # if the count parameter is set
            if count != 1:
                # create a new name by adding the counter to the original name
                name = original_name + str(i)

            # generate the OpenGL buffers (VBO) for each data type
            self.vertex_vbos[name] = glGenBuffers(1)
            self.normal_vbos[name] = glGenBuffers(1)
            self.uv_vbos[name] = glGenBuffers(1)
            # generate the OpenGL buffer (VAO) to store all the data
            self.vaos[name] = glGenVertexArrays(1)

            # store the vertices count
            self.vertices_count[name] = len(formatted_vertices) / 3

            # bind the VAO
            glBindVertexArray(self.vaos[name])

            # bind the vertex VBO
            glBindBuffer(GL_ARRAY_BUFFER, self.vertex_vbos[name])
            # store the data into the VBO
            glBufferData(GL_ARRAY_BUFFER, formatted_vertices.nbytes, formatted_vertices, GL_STATIC_DRAW)
            # enable the index 0 of the VAO
            glEnableVertexAttribArray(0)
            # store the data from the VBO in the VAO
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

            # repeat for normals
            glBindBuffer(GL_ARRAY_BUFFER, self.normal_vbos[name])
            glBufferData(GL_ARRAY_BUFFER, formatted_normals.nbytes, formatted_normals, GL_STATIC_DRAW)
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

            # and UVs
            glBindBuffer(GL_ARRAY_BUFFER, self.uv_vbos[name])
            glBufferData(GL_ARRAY_BUFFER, formatted_uvs.nbytes, formatted_uvs, GL_STATIC_DRAW)
            glEnableVertexAttribArray(2)
            glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))     

            # initialize the transformation variables for the new mesh
            self.positions[name] = glm.vec3(0.0)
            self.rotations[name] = glm.vec3(0.0)
            self.scales[name] = glm.vec3(1.0)
            self.model_matrices[name] = glm.mat4(1.0)

    # method to place the mesh in a specific spot
    def place(self, name, x, y, z):
        self.positions[name] = glm.vec3(x, y, z)
        self._calculate_model_matrix(name)

    # method to move a mesh by a certain vector
    def move(self, name, x, y, z):
        self.positions[name] += glm.vec3(x, y, z)
        self._calculate_model_matrix(name)
    
    # function to rotate the mesh
    def rotate(self, name, x, y, z):
        self.rotations[name] = glm.vec3(x, y, z)
        self._calculate_model_matrix(name)

    # function to scale the mesh
    def scale(self, name, x, y, z):
        self.scales[name] = glm.vec3(x, y, z)
        self._calculate_model_matrix(name)

    # function to calculate the model matrix after a transformation
    def _calculate_model_matrix(self, name):
        # reset the model matrix
        self.model_matrices[name] = glm.mat4(1)
        # calculate the translation
        self.model_matrices[name] = glm.translate(self.model_matrices[name], self.positions[name])
        # calculate the rotation by every axis
        self.model_matrices[name] = glm.rotate(self.model_matrices[name], glm.radians(self.rotations[name].x), glm.vec3(1.0, 0.0, 0.0))
        self.model_matrices[name] = glm.rotate(self.model_matrices[name], glm.radians(self.rotations[name].y), glm.vec3(0.0, 1.0, 0.0))
        self.model_matrices[name] = glm.rotate(self.model_matrices[name], glm.radians(self.rotations[name].z), glm.vec3(0.0, 0.0, 1.0))
        # calculate the scale
        self.model_matrices[name] = glm.scale(self.model_matrices[name], self.scales[name])

    # method to obtain an OpenGL ready matrix
    def get_ogl_matrix(self, name):
        return(glm.value_ptr(self.model_matrices[name]))
