# main libraries imports
from OpenGL.GL import *
import numpy as np
from PIL import Image
import pywavefront
import glm
import operator

# custom modules imports
from utils.Singleton import Singleton
from utils.colors import colors
from utils.Timer import Timer
from renderer.model.Model import Model
from renderer.shader.Shader import Shader
from renderer.camera.Camera import Camera
from renderer.instance import Instance

# method to setup and handle all the required data for the renderer
class RendererManager(metaclass=Singleton):
    # constructor method
    def __init__(self):
        # dictionary to keep track of model objects
        self.models = dict()

        self.single_render_models = []

        # fields for screen dimensions
        self.width = 800
        self.height = 600

        # dictionaries of OpenGL VBOs for vertex data (vertex, normal, uv)
        self.vertex_vbos = dict()
        self.normal_vbos = dict()
        self.uv_vbos = dict()
        # dictionary of OpenGL VAO for vertex data
        self.vaos = dict()

        self.instances = dict()

        self.textures = dict()

        self.materials = dict()

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

        self.fov = 60.0
        self.projection_matrix = glm.perspective(glm.radians(self.fov), float(self.width)/float(self.height), 0.1, 10000.0)

        self.to_update = True

        # setup the required data for the engine
        self._setup_entities()

        self._setup_render_framebuffer()
        
    # method to setup the required entities for the engine
    def _setup_entities(self):
        # compilation of necessary shaders for the engine
        self.shaders["lighting"] = Shader("./assets/shaders/lighting/lighting.vert", "./assets/shaders/lighting/lighting.frag")
        self.shaders["white"] = Shader("./assets/shaders/white/white.vert", "./assets/shaders/white/white.frag")
        self.shaders["screen"] = Shader("./assets/shaders/screen/screen.vert", "./assets/shaders/screen/screen.frag")
        self.shaders["lighting_instanced"] = Shader("assets/shaders/lighting_instanced/lighting_instanced.vert", "assets/shaders/lighting_instanced/lighting_instanced.frag")
        
        self.new_mesh("screen_quad", "./assets/models/quad.obj")
        self.new_mesh("default_mesh", "assets/models/box.obj")

        self.new_material("default_material", (0.2, 0.2, 0.2), (0.6, 0.6, 0.6), (1.0, 1.0, 1.0), 1.0)
        self.new_material("light_color", (0.2, 0.2, 0.2), (0.5, 0.5, 0.5), (1.0, 1.0, 1.0), 1.0)

        # creation of a camera object
        self.camera = Camera()

        # creation of a light source object (just a position for now)
        self.light_source = glm.vec3(10, 10, 10)

    # method for setting up the render framebuffer
    def _setup_render_framebuffer(self):
        # generate the framebuffer
        self.render_framebuffer = glGenFramebuffers(1)
        # bind it as the current framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self.render_framebuffer)
        
        # generate the texture to render the image to
        self.color_render_texture = glGenTextures(1)
        # bind it to as the current texture
        glBindTexture(GL_TEXTURE_2D, self.color_render_texture)
        # generate the texture with the screen dimensions
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # generate the renderbuffer to render the depth and stencil information
        self.depth_stencil_render_renderbuffer = glGenRenderbuffers(1)
        # bind the current renderbuffer
        glBindRenderbuffer(GL_RENDERBUFFER, self.depth_stencil_render_renderbuffer)
        # create the storage for the renderbuffer
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, self.width, self.height)

        # bind the color texture and depth/stencil renderbuffer to the framebuffer
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.color_render_texture, 0)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, self.depth_stencil_render_renderbuffer)
        
        # check that the framebuffer was correctly initialized
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            print("framebuffer error")

        # rebind the default framebuffer 
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # method to create a new mesh, a count can be specified to generate more than 1 mesh with the same 3D model
    # count argument is now deprecated
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

    # method to generate a new texture (needs double checking if it's correct)
    def new_texture(self, name, filepath):
        # generate a new OpenGL texture
        self.textures[name] = glGenTextures(1)
        # bind the newly created texture
        glBindTexture(GL_TEXTURE_2D, self.textures[name])

        # open the image using pillow, flip the image to make it compatible with OpenGL
        im = Image.open(filepath).transpose(Image.FLIP_TOP_BOTTOM)
        # get the image data
        imdata = np.fromstring(im.tobytes(), np.uint8)

        # setup the texture parameters
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)

        # pass the image data to the texture
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, im.size[0], im.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, imdata)

    # method to create a new material, composed of ambient, diffuse, specular colors and shininess value
    def new_material(self, name, ambient, diffuse, specular, shininess):
        self.materials[name] = dict()
        self.materials[name]["ambient"] = glm.vec3(ambient[0], ambient[1], ambient[2])
        self.materials[name]["diffuse"] = glm.vec3(diffuse[0], diffuse[1], diffuse[2])
        self.materials[name]["specular"] = glm.vec3(specular[0], specular[1], specular[2])
        self.materials[name]["shininess"] = shininess

    # method to create a new model
    def new_model(self, name, mesh = "default_mesh", shader = "", texture = "", material = "default_material", count = 1):
        # keep track of the original name of the model (in case there is mulitple counts)
        original_name = name

        # iterate through all the new models
        for i in range(count):
            # if there is more than one model to be created
            if count != 1:
                # append a number to the name
                name = original_name + str(i)

            # create a new model object
            self.models[name] = Model(name, mesh, texture, shader, material)
            self.single_render_models.append(self.models[name])

            # initialize the transformation variables for the new mesh
            self.positions[name] = glm.vec3(0.0)
            self.rotations[name] = glm.vec3(0.0)
            self.scales[name] = glm.vec3(1.0)
            self.model_matrices[name] = glm.mat4(1.0)

    def new_instance(self, name, mesh = "", shader = ""):
        self.instances[name] = Instance()

        if mesh == "":
            print(f"{colors.ERROR}Couldn't create the instance, Mesh not set{colors.ENDC}")
            return
        
        if shader == "":
            print(f"{colors.ERROR}Couldn't create the instance, Shader not set{colors.ENDC}")
            return

        instance = self.instances[name]

        instance.mesh = mesh
        instance.shader = shader

        self._initialize_instance(name)

    def _initialize_instance(self, name):
        instance = self.instances[name]

        instance.model_matrices = []

        for model in instance.models:
            instance.model_matrices.append(self.model_matrices[model.name])

        # temporary list of model matrices
        formatted_model_matrices = []

        # extract the values of the model matrices
        for model_mat in instance.model_matrices:
            for col in model_mat:
                for value in col:
                    formatted_model_matrices.append(value)


        # convert the list into an array of 32bit floats
        formatted_model_matrices = np.array(formatted_model_matrices, dtype=np.float32)
        # get the size in bits of an item in the matrices list
        item_size = formatted_model_matrices.itemsize

        # if the model matrices vbo already exists, delete it
        if instance.model_matrices_vbo != None:
            glDeleteBuffers(1, instance.model_matrices_vbo)

        # generate a new buffer for the model matrices
        instance.model_matrices_vbo = glGenBuffers(1)
        # bind the new buffer
        glBindBuffer(GL_ARRAY_BUFFER, instance.model_matrices_vbo)
        # pass the data to the buffer
        glBufferData(GL_ARRAY_BUFFER, item_size * len(formatted_model_matrices), formatted_model_matrices, GL_STATIC_DRAW)
        # glBindBuffer(GL_ARRAY_BUFFER, 0)

        # if the vao already exists, delete it
        if instance.vao != None:
            glDeleteVertexArrays(1, instance.vao)

        # create a new VAO
        instance.vao = glGenVertexArrays(1)
        # bind the newly created VAO
        glBindVertexArray(instance.vao)

        # bind the vertex vbo of the mesh of the instance
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_vbos[instance.mesh])
        # enable the index 0 of the VAO
        glEnableVertexAttribArray(0)
        # link the VBO to the index 0 of the VAO and interpret it as 3 floats
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        # bind the normals vbo of the mesh of the instance
        glBindBuffer(GL_ARRAY_BUFFER, self.normal_vbos[instance.mesh])
        # enable the index 1 of the VAO
        glEnableVertexAttribArray(1)
        # link the VBO to the index 1 of the VAO and interpret it as 3 floats
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        # bind the uv vbo of the mesh of the instance
        glBindBuffer(GL_ARRAY_BUFFER, self.uv_vbos[instance.mesh])
        # enable the index 2 of the VAO
        glEnableVertexAttribArray(2)
        # link the VBO to the index 2 of the VAO and interpret it as 2 floats
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        # bind the matrices vbo of the models of the instance
        glBindBuffer(GL_ARRAY_BUFFER, instance.model_matrices_vbo)
        # enable the index 3 of the VAO
        glEnableVertexAttribArray(3)
        # link the beginning of the VBO to the index 3 of the VAO and interpret it as 4 floats
        glVertexAttribPointer(3, 4, GL_FLOAT, GL_FALSE, item_size * 16, ctypes.c_void_p(0))

        # enable the index 4 of the VAO
        glEnableVertexAttribArray(4)
        # link the second column of the matrix to the index 4 of the VAO and interpret it as 4 floats
        glVertexAttribPointer(4, 4, GL_FLOAT, GL_FALSE, item_size * 16, ctypes.c_void_p(formatted_model_matrices.itemsize * 4 * 1))

        # enable the index 5 of the VAO
        glEnableVertexAttribArray(5)
        # link the third column of the matrix to the index 5 of the VAO and intepret it as 4 floats
        glVertexAttribPointer(5, 4, GL_FLOAT, GL_FALSE, item_size * 16, ctypes.c_void_p(formatted_model_matrices.itemsize * 4 * 2))

        # enable the index 6 of the VAO
        glEnableVertexAttribArray(6)
        # link the fourth column of the matrix to the index 6 of the VAO and intepret it as 4 floats
        glVertexAttribPointer(6, 4, GL_FLOAT, GL_FALSE, item_size * 16, ctypes.c_void_p(formatted_model_matrices.itemsize * 4 * 3))

        # tell OpenGL that the indices 3, 4, 5 and 6 of the VAO need to change after every call
        glVertexAttribDivisor(3, 1)
        glVertexAttribDivisor(4, 1)
        glVertexAttribDivisor(5, 1)
        glVertexAttribDivisor(6, 1)

        # bind to the default VAO
        glBindVertexArray(0)

        instance.to_update = False

    def add_model_to_instance(self, model, instance):
        name = model
        model = self.models[model]
        instance = self.instances[instance]

        instance.models.append(model)
        instance.model_matrices.append(self.model_matrices[name])

        self.single_render_models.remove(model)

        model.in_instance = True
        instance.to_update = True

    def remove_model_from_instance(self, model, instance):
        name = model
        model = self.models[model]
        instance = self.instances[instance]

        instance.models.remove(model)
        instance.model_matrices.remove(self.model_matrices[name])

        self.single_render_models.append(model)

        model.in_instance = False
        instance.to_update = True

    def set_instance_mesh(self, instance, mesh):
        self.instances[instance].mesh = mesh
        self.instances[instance].to_update = True

    def set_instance_shader(self, instance, shader):
        self.instances[instance].shader = shader
        self.instances[instance].to_update = True

    def light_material(self):
        return(self.materials["light_color"])

    # method to place the mesh in a specific spot
    def place(self, name, x, y, z):
        self.positions[name] = glm.vec3(x, y, z)
        self._calculate_model_matrix(name)
        self._check_instance_update(name)        

    # method to move a mesh by a certain vector
    def move(self, name, x, y, z):
        self.positions[name] += glm.vec3(x, y, z)
        self._calculate_model_matrix(name)
        self._check_instance_update(name)
    
    # function to rotate the mesh
    def rotate(self, name, x, y, z):
        self.rotations[name] = glm.vec3(x, y, z)
        self._calculate_model_matrix(name)
        self._check_instance_update(name)

    # function to scale the mesh
    def scale(self, name, x, y, z):
        self.scales[name] = glm.vec3(x, y, z)
        self._calculate_model_matrix(name)
        self._check_instance_update(name)

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

    def get_ogl_projection_matrix(self):
        return(glm.value_ptr(self.projection_matrix))

    # method to update the dimensions of the screen
    def update_dimensions(self, width, height):
        # update the internal dimensions
        self.width = int(width)
        self.height = int(height)

        self.projection_matrix = glm.perspective(glm.radians(self.fov), float(self.width)/float(self.height), 0.1, 10000.0)

        # bind the render framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self.render_framebuffer)

        # delete the renderbuffer and the texture of the framebuffer
        glDeleteRenderbuffers(1, [self.depth_stencil_render_renderbuffer])
        glDeleteTextures(1, [self.color_render_texture])

        # create a new color texture and depth/stencil renderbuffer with the updated dimensions
        self.color_render_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.color_render_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        self.depth_stencil_render_renderbuffer = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, self.depth_stencil_render_renderbuffer)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, self.width, self.height)

        # bind the new texture and renderbuffer to the framebuffer
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.color_render_texture, 0)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, self.depth_stencil_render_renderbuffer)

        # bind the default framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)


    def _check_instance_update(self, name):
        if not self.models[name].in_instance:
            return
        
        for instance in self.instances.values():
            if self.models[name] in instance.models:
                instance.to_update = True

    def update(self):
        for name, instance in self.instances.items():
            if instance.to_update:
                self._initialize_instance(name)