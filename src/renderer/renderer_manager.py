# main libraries imports
from OpenGL.GL import *
import numpy as np
from PIL import Image
import pywavefront
import glm
from PIL import Image
import numpy as np
import json

# custom modules imports
from utils.singleton import Singleton
from utils.colors import colors
from utils.vbo_indexer import *
from utils.messages import *
from utils.timer import Timer

from renderer.model.model import Model
from renderer.material.material import Material
from renderer.shader.shader import Shader
from renderer.camera.camera import Camera
from renderer.instance import Instance

# method to setup and handle all the required data for the renderer
class RendererManager(metaclass=Singleton):
    # constructor method
    def __init__(self):
        glEnable(GL_MULTISAMPLE)
        timer = Timer()
        # dictionary to keep track of model objects
        self.models = dict()
        self.changed_models = dict()

        # list of models to be rendered normally
        self.single_render_models = []

        # fields for screen dimensions
        self.width = 800
        self.height = 600

        # dictionaries of OpenGL VBOs for vertex data (vertex, normal, uv)
        self.vertex_vbos = dict()
        self.normal_vbos = dict()
        self.uv_vbos = dict()
        # dictionary of OpenGL EBOs for index data
        self.ebos = dict()
        # dictionary of OpenGL VAO for vertex data
        self.vaos = dict()

        # dictionary of instance objects
        self.instances = dict()

        # dictionary of textures
        self.textures = dict()

        # dictionary of material objects
        self.materials = dict()

        # dictionary of model matrices
        self.model_matrices = dict()
        # dictionary of number of vertices per mesh
        self.vertices_count = dict()
        # dictionary of number of indices per mesh
        self.indices_count = dict()
        # dictionary of trasformation factors of the meshes
        self.positions = dict()
        self.rotations = dict()
        self.scales = dict()

        # dictionary of shaders compiled for the engine
        self.shaders = dict()

        # create the projection matrix for rendering
        self.fov = 60.0
        self.projection_matrix = glm.perspective(glm.radians(self.fov), float(self.width)/float(self.height), 0.1, 10000.0)

        # variable to keep track of weather or not the renderer manager should update
        self.to_update = True

        self.post_processing_shaders = []
        self.available_post_processing_shaders = []

        self.render_states = dict()
        self.render_states["depth_of_field"] = True
        self.render_states["post_processing"] = True

        self.max_samples = glGetIntegerv(GL_MAX_COLOR_TEXTURE_SAMPLES)
        self.samples = self.max_samples

        self.lights = dict()
        self.light_colors = []
        self.light_positions = []
        self.light_strengths = []
        self.lights_count = 0

        # setup the required data for the engine
        self._setup_entities()

        # setup the rendering framebuffer
        self._setup_render_framebuffer()

        self._setup_skybox()

        print_success("Initialized Renderer Manager in " + str(round(timer.elapsed() / 1000, 2)) + "s")
        
    # method to setup the required entities for the engine
    def _setup_entities(self):
        # compilation of necessary shaders for the engine
        self.shaders["lighting"] = Shader("./assets/shaders/lighting/lighting.vert", "./assets/shaders/lighting/lighting.frag")
        self.shaders["white"] = Shader("./assets/shaders/white/white.vert", "./assets/shaders/white/white.frag")
        self.shaders["screen"] = Shader("./assets/shaders/screen/screen.vert", "./assets/shaders/screen/screen.frag")
        self.shaders["lighting_instanced"] = Shader("assets/shaders/lighting_instanced/lighting_instanced.vert", "assets/shaders/lighting_instanced/lighting_instanced.frag")
        self.shaders["depth"] = Shader("assets/shaders/depth/depth.vert", "assets/shaders/depth/depth.frag")
        self.shaders["depth_of_field"] = Shader("assets/shaders/depth_of_field/depth_of_field.vert",
                                                "assets/shaders/depth_of_field/depth_of_field.frag")
        self.shaders["msaa"] = Shader("assets/shaders/msaa/msaa.vert", "assets/shaders/msaa/msaa.frag")
        self.shaders["pbr"] = Shader("assets/shaders/pbr/pbr.vert", "assets/shaders/pbr/pbr.frag")
        self.shaders["pbr_instanced"] = Shader("assets/shaders/pbr_instanced/pbr_instanced.vert", "assets/shaders/pbr_instanced/pbr_instanced.frag")
        
        self.shaders["post_processing/inverted_colors"] = Shader("assets/shaders/post_processing/inverted_colors/inverted_colors.vert",
                                                                 "assets/shaders/post_processing/inverted_colors/inverted_colors.frag")

        self.shaders["post_processing/black_white"] = Shader("assets/shaders/post_processing/black_white/black_white.vert",
                                                             "assets/shaders/post_processing/black_white/black_white.frag")
        
        self.shaders["post_processing/sharpen"] = Shader("assets/shaders/post_processing/sharpen/sharpen.vert",
                                                         "assets/shaders/post_processing/sharpen/sharpen.frag")

        self.shaders["post_processing/blur"] = Shader("assets/shaders/post_processing/blur/blur.vert",
                                                      "assets/shaders/post_processing/blur/blur.frag")

        self.shaders["post_processing/wave"] = Shader("assets/shaders/post_processing/wave/wave.vert",
                                                      "assets/shaders/post_processing/wave/wave.frag")

        self.shaders["post_processing/gaussian_blur"] = Shader("assets/shaders/post_processing/gaussian_blur/gaussian_blur.vert",
                                                               "assets/shaders/post_processing/gaussian_blur/gaussian_blur.frag")

        self.shaders["post_processing/dilation"] = Shader("assets/shaders/post_processing/dilation/dilation.vert",
                                                          "assets/shaders/post_processing/dilation/dilation.frag")
        
        self.shaders["post_processing/fixed_depth_of_field"] = Shader("assets/shaders/post_processing/fixed_depth_of_field/fixed_depth_of_field.vert",
                                                                      "assets/shaders/post_processing/fixed_depth_of_field/fixed_depth_of_field.frag")

        self.available_post_processing_shaders.append("post_processing/black_white")
        self.available_post_processing_shaders.append("post_processing/inverted_colors")
        self.available_post_processing_shaders.append("post_processing/sharpen")
        self.available_post_processing_shaders.append("post_processing/blur")
        self.available_post_processing_shaders.append("post_processing/wave")
        self.available_post_processing_shaders.append("post_processing/gaussian_blur")
        self.available_post_processing_shaders.append("post_processing/dilation")
        self.available_post_processing_shaders.append("post_processing/fixed_depth_of_field")

        self.new_json_mesh("screen_quad", "assets/models/default/quad.json")
        self.new_json_mesh("default", "assets/models/default/box.json")

        self.new_material("default", *(0.2, 0.2, 0.2), *(0.6, 0.6, 0.6), *(1.0, 1.0, 1.0), 1.0)
        self.new_material("light_color", *(0.2, 0.2, 0.2), *(1.0, 1.0, 1.0), *(1.0, 1.0, 1.0), 1.0)

        self.new_texture("default", "assets/textures/uv-maptemplate.jpg")

        # creation of a camera object
        self.camera = Camera()

        # creation of a light source object (just a position for now)
        # self.lights["main"] = Light()
        self.new_light("main")

    # method for setting up the render framebuffer
    def _setup_render_framebuffer(self):
        # generate the framebuffer
        self.render_framebuffer = glGenFramebuffers(1)
        # bind it as the current framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self.render_framebuffer)
        
        # generate the texture to render the image to
        self.multisample_render_texture = glGenTextures(1)
        # bind it to as the current texture
        glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, self.multisample_render_texture)
        # generate the texture with the screen dimensions
        # glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexImage2DMultisample(GL_TEXTURE_2D_MULTISAMPLE, self.max_samples, GL_RGB, self.width, self.height, GL_FALSE)
        # glTexStorage2DMultisample(GL_TEXTURE_2D_MULTISAMPLE, self.max_samples, GL_RGB8, self.width, self.height, GL_TRUE)
        
        # glTexParameteri(GL_TEXTURE_2D_MULTISAMPLE, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        # glTexParameteri(GL_TEXTURE_2D_MULTISAMPLE, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # glTexParameteri(GL_TEXTURE_2D_MULTISAMPLE, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        # glTexParameteri(GL_TEXTURE_2D_MULTISAMPLE, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        # glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, 0)

        # generate the renderbuffer to render the depth and stencil information
        # self.depth_stencil_render_renderbuffer = glGenRenderbuffers(1)
        # bind the current renderbuffer
        # glBindRenderbuffer(GL_RENDERBUFFER, self.depth_stencil_render_renderbuffer)
        # create the storage for the renderbuffer
        # glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, self.width, self.height)

        self.depth_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, self.depth_texture)
        # glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.width, self.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexImage2DMultisample(GL_TEXTURE_2D_MULTISAMPLE, self.max_samples, GL_DEPTH_COMPONENT, self.width, self.height, GL_FALSE)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # bind the color texture and depth/stencil renderbuffer to the framebuffer
        # glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.color_render_texture, 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D_MULTISAMPLE, self.multisample_render_texture, 0)
        # glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, self.depth_stencil_render_renderbuffer)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D_MULTISAMPLE, self.depth_texture, 0)

        # check that the framebuffer was correctly initialized
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            error = glCheckFramebufferStatus(GL_FRAMEBUFFER)
            print("main framebuffer error")
            # print(glCheckFramebufferStatus(GL_FRAMEBUFFER))
            if error == GL_FRAMEBUFFER_UNDEFINED:
                print("GL_FRAMEBUFFER_UNDEFINED")
            if error == GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT:
                print("GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT")
            if error == GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT:
                print("GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT")
            if error == GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER:
                print("GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER")
            if error == GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER:
                print("GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER")
            if error == GL_FRAMEBUFFER_UNSUPPORTED:
                print("GL_FRAMEBUFFER_UNSUPPORTED")
            if error == GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE:
                print("GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE")
            if error == GL_FRAMEBUFFER_INCOMPLETE_LAYER_TARGETS:
                print("GL_FRAMEBUFFER_INCOMPLETE_LAYER_TARGETS")


        # rebind the default framebuffer 
        glBindFramebuffer(GL_FRAMEBUFFER, 0)



        self.solved_framebuffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.solved_framebuffer)
        self.solved_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.solved_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        self.solved_depth_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.solved_depth_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.width, self.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.solved_texture, 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.solved_depth_texture, 0)

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            print("framebuffer error")


        self.blurred_framebuffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.blurred_framebuffer)
        self.blurred_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.blurred_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        # self.blurred_depth_renderbuffer = glGenRenderbuffers(1)
        # glBindRenderbuffer(GL_RENDERBUFFER, self.blurred_depth_renderbuffer)
        # glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, self.width, self.height)
        
        self.blurred_depth_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.blurred_depth_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.width, self.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.blurred_texture, 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.blurred_depth_texture, 0)
        # glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, self.blurred_depth_renderbuffer)

        # check that the framebuffer was correctly initialized
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            print("framebuffer error")

        # rebind the default framebuffer 
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # self.depth_texture = glGenTextures(1)
        # glBindTexture(GL_TEXTURE_2D, self.depth_texture)
        # glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.width, self.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)


    # method for setting up the skybox
    def _setup_skybox(self):
        # directory of the skybox files
        # filepath = "./assets/textures/Epic_BlueSunset/"
        filepath = "./assets/textures/dark/"

        # list of faces
        texture_faces = []
        texture_faces.append(filepath + "left.png")
        texture_faces.append(filepath + "right.png")
        texture_faces.append(filepath + "top.png")
        texture_faces.append(filepath + "bottom.png")
        texture_faces.append(filepath + "back.png")
        texture_faces.append(filepath + "front.png")
            
        # generate a cubemap texture
        self.skybox_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.skybox_texture)

        # iterate through the faces, load the image and store it in the right face of the cubemap
        for i in range(len(texture_faces)):
            im = Image.open(texture_faces[i])#.transpose(Image.FLIP_TOP_BOTTOM)

            # flip the top and bottom images
            if i == 2 or i == 3:
                im = im.transpose(Image.FLIP_LEFT_RIGHT)
                im = im.transpose(Image.FLIP_TOP_BOTTOM)

            # get the data of the loaded face image
            imdata = np.fromstring(im.tobytes(), np.uint8)

            # store the data of the image in the cubemap texture
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB, im.size[0], im.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, imdata)

        # set the texture behaviour
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        # load the skybox rendering shader
        self.shaders["skybox"] = Shader("assets/shaders/skybox/skybox.vert", "assets/shaders/skybox/skybox.frag")

    # --------------------------- Creating Components ----------------------------------

    # method to create a new mesh, a count can be specified to generate more than 1 mesh with the same 3D model
    def new_mesh(self, name, file_path):
        timer = Timer()
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

        # format the lists into np.arrays of type float 32bit
        formatted_vertices = np.array(formatted_vertices, dtype=np.float32)
        formatted_normals = np.array(formatted_normals, dtype=np.float32)
        formatted_uvs = np.array(formatted_uvs, dtype=np.float32)

        # convert the lists into indiced lists and obtain an indices list for indexed rendering
        # indices, indiced_vertices, indiced_normals, indiced_uvs = index_vertices(formatted_vertices, formatted_normals, formatted_uvs)
        indices, indiced_vertices, indiced_normals, indiced_uvs = index_vertices(formatted_vertices, formatted_normals, formatted_uvs)

        # keep track of the indices count
        self.indices_count[name] = len(indices)

        # convert the indexed lists into indexed arrays of type float 32bit
        indiced_vertices = np.array(indiced_vertices, dtype=np.float32)
        indiced_normals = np.array(indiced_normals, dtype=np.float32)
        indiced_uvs = np.array(indiced_uvs, dtype=np.float32)

        # convert the list of indices into an array of indices of type unsigned int 32bit
        indices = np.array(indices, dtype=np.uint32)

        # generate the OpenGL buffers (VBO) for each data type
        self.vertex_vbos[name] = glGenBuffers(1)
        self.normal_vbos[name] = glGenBuffers(1)
        self.uv_vbos[name] = glGenBuffers(1)
        self.ebos[name] = glGenBuffers(1)
        # generate the OpenGL buffer (VAO) to store all the data
        self.vaos[name] = glGenVertexArrays(1)

        # store the vertices count
        self.vertices_count[name] = len(formatted_vertices) / 3

        # bind the VAO
        glBindVertexArray(self.vaos[name])

        # bind the vertex VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_vbos[name])
        # store the data into the VBO
        glBufferData(GL_ARRAY_BUFFER, indiced_vertices.nbytes, indiced_vertices, GL_STATIC_DRAW)
        # enable the index 0 of the VAO
        glEnableVertexAttribArray(0)
        # store the data from the VBO in the VAO
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        # repeat for normals
        glBindBuffer(GL_ARRAY_BUFFER, self.normal_vbos[name])
        glBufferData(GL_ARRAY_BUFFER, indiced_normals.nbytes, indiced_normals, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        # and UVs
        glBindBuffer(GL_ARRAY_BUFFER, self.uv_vbos[name])
        glBufferData(GL_ARRAY_BUFFER, indiced_uvs.nbytes, indiced_uvs, GL_STATIC_DRAW)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        # pass the data for the element array buffer of indices
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebos[name])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        print_info("Created mesh: " + name + " in " + str(round(timer.elapsed() / 1000, 2)) + "s")

    def new_json_mesh(self, name, file_path):
        timer = Timer()

        f = open(file_path, "r")
        data = json.load(f)

        

        # keep track of the indices count
        self.indices_count[name] = len(data["indices"])

        # convert the indexed lists into indexed arrays of type float 32bit
        indiced_vertices = np.array(data["vertices"], dtype=np.float32)
        indiced_normals = np.array(data["normals"], dtype=np.float32)
        indiced_uvs = np.array(data["uvs"], dtype=np.float32)

        # convert the list of indices into an array of indices of type unsigned int 32bit
        indices = np.array(data["indices"], dtype=np.uint32)

        # generate the OpenGL buffers (VBO) for each data type
        self.vertex_vbos[name] = glGenBuffers(1)
        self.normal_vbos[name] = glGenBuffers(1)
        self.uv_vbos[name] = glGenBuffers(1)
        self.ebos[name] = glGenBuffers(1)
        # generate the OpenGL buffer (VAO) to store all the data
        self.vaos[name] = glGenVertexArrays(1)

        # store the vertices count
        self.vertices_count[name] = len(indiced_vertices) / 3

        # bind the VAO
        glBindVertexArray(self.vaos[name])

        # bind the vertex VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_vbos[name])
        # store the data into the VBO
        glBufferData(GL_ARRAY_BUFFER, indiced_vertices.nbytes, indiced_vertices, GL_STATIC_DRAW)
        # enable the index 0 of the VAO
        glEnableVertexAttribArray(0)
        # store the data from the VBO in the VAO
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        # repeat for normals
        glBindBuffer(GL_ARRAY_BUFFER, self.normal_vbos[name])
        glBufferData(GL_ARRAY_BUFFER, indiced_normals.nbytes, indiced_normals, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        # and UVs
        glBindBuffer(GL_ARRAY_BUFFER, self.uv_vbos[name])
        glBufferData(GL_ARRAY_BUFFER, indiced_uvs.nbytes, indiced_uvs, GL_STATIC_DRAW)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        # pass the data for the element array buffer of indices
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebos[name])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        print_info("Created mesh: " + name + " in " + str(round(timer.elapsed() / 1000, 2)) + "s")

    def new_shader(self, name, vert_path, frag_path):
        self.shaders[name] = Shader(vert_path, frag_path)

    def new_light(self, name, light_position = (0.0, 0.0, 0.0), light_color = (1.0, 1.0, 1.0), light_strength = 8.0):
        self.lights_count += 1

        self.lights[name] = self.lights_count - 1

        self.light_positions.append(light_position[0])
        self.light_positions.append(light_position[1])
        self.light_positions.append(light_position[2])
        
        self.light_colors.append(light_color[0])
        self.light_colors.append(light_color[1])
        self.light_colors.append(light_color[2])

        self.light_strengths.append(light_strength)

    # method to generate a new texture (needs double checking if it's correct)
    def new_texture(self, name, filepath):
        # generate a new OpenGL texture
        self.textures[name] = glGenTextures(1)
        # bind the newly created texture
        glBindTexture(GL_TEXTURE_2D, self.textures[name])

        # open the image using pillow, flip the image to make it compatible with OpenGL
        # im = Image.open(filepath).transpose(Image.FLIP_TOP_BOTTOM)
        # # get the image data
        # # imdata = np.fromstring(im.tobytes(), np.uint8)
        # imdata = im.convert("RGBA").tobytes()

        # setup the texture parameters
        # glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        # pass the image data to the texture
        # glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, im.width, im.height, 0, GL_RGB, GL_UNSIGNED_BYTE, imdata)

        image = Image.open(filepath)
        convert = image.convert("RGBA")
        image_data = convert.transpose(Image.FLIP_TOP_BOTTOM).tobytes()
        width = image.width
        height = image.height
        image.close()

        glBindTexture(GL_TEXTURE_2D, self.textures[name])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

    # method to create a new material, composed of ambient, diffuse, specular colors and shininess value
    def new_material(self,
                     name,
                     ambient_r = 1.0, ambient_g = 1.0, ambient_b = 1.0,
                     diffuse_r = 1.0, diffuse_g = 1.0, diffuse_b = 1.0,
                     specular_r = 1.0, specular_g = 1.0, specular_b = 1.0,
                     shininess = 1.0,
                     roughness = 0.5,
                     metallic = 0.5):
        self.materials[name] = Material(name,
                                        ambient_r, ambient_g, ambient_b,
                                        diffuse_r, diffuse_g, diffuse_b,
                                        specular_r, specular_g, specular_b,
                                        shininess,
                                        roughness,
                                        metallic)

    # method to create a new model
    def new_model(self, name, mesh = "default", shader = "default", texture = "default", material = "default", count = 1):
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
            self.materials[material].add_model(self.models[name])

            self.single_render_models.append(self.models[name])

            # initialize the transformation variables for the new mesh
            self.positions[name] = glm.vec3(0.0)
            self.rotations[name] = glm.vec3(0.0)
            self.scales[name] = glm.vec3(1.0)
            self.model_matrices[name] = glm.mat4(1.0)

    # method to create a new instance
    def new_instance(self, name, mesh = "", shader = ""):
        # check if the mesh and shader fields have been provided
        if mesh == "":
            print(f"{colors.ERROR}Couldn't create the instance, Mesh not set{colors.ENDC}")
            return
        
        if shader == "":
            print(f"{colors.ERROR}Couldn't create the instance, Shader not set{colors.ENDC}")
            return

        # create a new instance object
        self.instances[name] = Instance()
        # get a reference to the newly created object
        instance = self.instances[name]

        # set the instance constants
        instance.mesh = mesh
        instance.shader = shader

        # intialize the instance
        self._initialize_instance(name)

    # method to initialize an instance, might move this inside the instance object
    def _initialize_instance(self, name):
        instance = self.instances[name]

        # temporary list of model matrices
        formatted_model_matrices = []

        # extract the values of the model matrices
        for model in instance.models:
            for col in self.model_matrices[model.name]:
                for value in col:
                    formatted_model_matrices.append(value)

        formatted_ambients = []
        formatted_diffuses = []
        formatted_speculars = []
        formatted_shininesses = []
        formatted_roughnesses = []
        formatted_metallicnesses = []

        for model in instance.models:
            material = self.materials[model.material]
            formatted_ambients.append(material.ambient[0])
            formatted_ambients.append(material.ambient[1])
            formatted_ambients.append(material.ambient[2])
            
            formatted_diffuses.append(material.diffuse[0])
            formatted_diffuses.append(material.diffuse[1])
            formatted_diffuses.append(material.diffuse[2])
            
            formatted_speculars.append(material.specular[0])
            formatted_speculars.append(material.specular[1])
            formatted_speculars.append(material.specular[2])

            formatted_shininesses.append(material.shininess)

            formatted_roughnesses.append(material.roughness)
            formatted_metallicnesses.append(material.metallic)

        formatted_ambients = np.array(formatted_ambients, dtype=np.float32)
        formatted_diffuses = np.array(formatted_diffuses, dtype=np.float32)
        formatted_speculars = np.array(formatted_speculars, dtype=np.float32)
        formatted_shininesses = np.array(formatted_shininesses, dtype=np.float32)
        formatted_roughnesses = np.array(formatted_roughnesses, dtype=np.float32)
        formatted_metallicnesses = np.array(formatted_metallicnesses, dtype=np.float32)
            
        # convert the list into an array of 32bit floats
        formatted_model_matrices = np.array(formatted_model_matrices, dtype=np.float32)
        # get the size in bits of an item in the matrices list
        float_size = formatted_model_matrices.itemsize

        instance.model_matrices = formatted_model_matrices
        instance.ambients = formatted_ambients
        instance.diffuses = formatted_diffuses
        instance.speculars = formatted_speculars
        instance.shininesses = formatted_shininesses
        instance.roughnesses = formatted_roughnesses
        instance.metallicnesses = formatted_metallicnesses

        # if the model matrices vbo already exists, delete it
        if instance.model_matrices_vbo != None:
            glDeleteBuffers(1, instance.model_matrices_vbo)

        # generate a new buffer for the model matrices
        instance.model_matrices_vbo = glGenBuffers(1)
        # bind the new buffer
        glBindBuffer(GL_ARRAY_BUFFER, instance.model_matrices_vbo)
        # pass the data to the buffer
        glBufferData(GL_ARRAY_BUFFER, float_size * len(formatted_model_matrices), formatted_model_matrices, GL_STREAM_DRAW)
        # glBindBuffer(GL_ARRAY_BUFFER, 0)

        if instance.ambient_vbo != None:
            instance.ambient_vbo = glGenBuffers(1)

        instance.ambient_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, instance.ambient_vbo)
        glBufferData(GL_ARRAY_BUFFER, float_size * len(formatted_ambients), formatted_ambients, GL_STATIC_DRAW)

        
        instance.diffuse_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, instance.diffuse_vbo)
        glBufferData(GL_ARRAY_BUFFER, float_size * len(formatted_diffuses), formatted_diffuses, GL_STATIC_DRAW)

        
        instance.specular_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, instance.specular_vbo)
        glBufferData(GL_ARRAY_BUFFER, float_size * len(formatted_speculars), formatted_speculars, GL_STATIC_DRAW)

        
        instance.shininess_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, instance.shininess_vbo)
        glBufferData(GL_ARRAY_BUFFER, float_size * len(formatted_shininesses), formatted_shininesses, GL_STATIC_DRAW)

        instance.roughness_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, instance.roughness_vbo)
        glBufferData(GL_ARRAY_BUFFER, float_size * len(formatted_roughnesses), formatted_roughnesses, GL_STATIC_DRAW)

        instance.metallic_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, instance.metallic_vbo)
        glBufferData(GL_ARRAY_BUFFER, float_size * len(formatted_metallicnesses), formatted_metallicnesses, GL_STATIC_DRAW)

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
        glVertexAttribPointer(3, 4, GL_FLOAT, GL_FALSE, float_size * 16, ctypes.c_void_p(0))

        # enable the index 4 of the VAO
        glEnableVertexAttribArray(4)
        # link the second column of the matrix to the index 4 of the VAO and interpret it as 4 floats
        glVertexAttribPointer(4, 4, GL_FLOAT, GL_FALSE, float_size * 16, ctypes.c_void_p(float_size * 4 * 1))

        # enable the index 5 of the VAO
        glEnableVertexAttribArray(5)
        # link the third column of the matrix to the index 5 of the VAO and intepret it as 4 floats
        glVertexAttribPointer(5, 4, GL_FLOAT, GL_FALSE, float_size * 16, ctypes.c_void_p(float_size * 4 * 2))

        # enable the index 6 of the VAO
        glEnableVertexAttribArray(6)
        # link the fourth column of the matrix to the index 6 of the VAO and intepret it as 4 floats
        glVertexAttribPointer(6, 4, GL_FLOAT, GL_FALSE, float_size * 16, ctypes.c_void_p(float_size * 4 * 3))

        # tell OpenGL that the indices 3, 4, 5 and 6 of the VAO need to change after every call
        glVertexBindingDivisor(3, 1)
        glVertexBindingDivisor(4, 1)
        glVertexBindingDivisor(5, 1)
        glVertexBindingDivisor(6, 1)

        glBindBuffer(GL_ARRAY_BUFFER, instance.ambient_vbo)
        glEnableVertexAttribArray(7)
        glVertexAttribPointer(7, 3, GL_FLOAT, GL_FALSE, float_size * 3, ctypes.c_void_p(0))

        glBindBuffer(GL_ARRAY_BUFFER, instance.diffuse_vbo)
        glEnableVertexAttribArray(8)
        glVertexAttribPointer(8, 3, GL_FLOAT, GL_FALSE, float_size * 3, ctypes.c_void_p(0))
        
        glBindBuffer(GL_ARRAY_BUFFER, instance.specular_vbo)
        glEnableVertexAttribArray(9)
        glVertexAttribPointer(9, 3, GL_FLOAT, GL_FALSE, float_size * 3, ctypes.c_void_p(0))
        
        glBindBuffer(GL_ARRAY_BUFFER, instance.shininess_vbo)
        glEnableVertexAttribArray(10)
        glVertexAttribPointer(10, 1, GL_FLOAT, GL_FALSE, float_size, ctypes.c_void_p(0))

        glBindBuffer(GL_ARRAY_BUFFER, instance.roughness_vbo)
        glEnableVertexAttribArray(11)
        glVertexAttribPointer(11, 1, GL_FLOAT, GL_FALSE, float_size, ctypes.c_void_p(0))

        glBindBuffer(GL_ARRAY_BUFFER, instance.metallic_vbo)
        glEnableVertexAttribArray(12)
        glVertexAttribPointer(12, 1, GL_FLOAT, GL_FALSE, float_size, ctypes.c_void_p(0))


        glVertexBindingDivisor(7, 1)
        glVertexBindingDivisor(8, 1)
        glVertexBindingDivisor(9, 1)
        glVertexBindingDivisor(10, 1)
        glVertexBindingDivisor(11, 1)
        glVertexBindingDivisor(12, 1)

        # bind to the default VAO
        glBindVertexArray(0)

    # ---------------------------- Modify Instances -----------------------------------

    # method to add a model to an instance
    def add_model_to_instance(self, model, instance):
        model_name = model
        instance_name = instance
        model = self.models[model]
        instance = self.instances[instance]

        instance.models.append(model)

        model_mat_values = []

        for col in self.model_matrices[model_name]:
            for value in col:
                model_mat_values.append(value)

        instance.model_matrices = np.append(instance.model_matrices, model_mat_values)

        instance.ambients = np.append(instance.ambients, self.materials[model.material].ambient)
        instance.diffuses = np.append(instance.diffuses, self.materials[model.material].diffuse)
        instance.speculars = np.append(instance.speculars, self.materials[model.material].specular)
        instance.shininesses = np.append(instance.shininesses, self.materials[model.material].shininess)

        self.single_render_models.remove(model)

        model.in_instance = instance_name
        instance.to_update["model_matrices"] = True
        instance.to_update["ambients"] = True
        instance.to_update["diffuses"] = True
        instance.to_update["speculars"] = True
        instance.to_update["shininesses"] = True

    def set_models_in_instance(self, models, instance_name):
        instance = self.instances[instance_name]
        instance.models = []

        for model in models:
            instance.models.append(self.models[model])
            self.single_render_models.remove(self.models[model])
            self.models[model].in_instance = instance_name

        self._initialize_instance(instance_name)

    def remove_model_from_instance(self, model, instance):
        name = model
        model = self.models[model]
        instance = self.instances[instance]

        instance.models.remove(model)
        # instance.model_matrices.pop(name)

        self.single_render_models.append(model)

        model.in_instance = ""
        instance.to_update["model_matrices"] = True

    def set_instance_mesh(self, instance, mesh):
        if mesh != self.instances[instance].mesh:
            self.instances[instance].set_mesh(mesh, self.vertex_vbos[mesh], self.normal_vbos[mesh], self.uv_vbo[mesh])
        # self.instances[instance].mesh = mesh
        # self.instances[instance].to_update = True

    def set_instance_shader(self, instance, shader):
        self.instances[instance].shader = shader
        # self.instances[instance].to_update = True

    # ---------------------------- Modify Models -------------------------------------

    # method to place the mesh in a specific spot
    def place(self, name, x, y, z):
        self.positions[name] = glm.vec3(x, y, z)
        self.changed_models[name] = True
        # self._calculate_model_matrix(name)
        # self._check_instance_update(name)     

    # method to move a mesh by a certain vector
    def move(self, name, x, y, z):
        self.positions[name] += glm.vec3(x, y, z)
        self.changed_models[name] = True
        # self._calculate_model_matrix(name)
        # self._check_instance_update(name)
    
    # method to rotate the mesh
    def rotate(self, name, x, y, z):
        self.rotations[name] = glm.vec3(x, y, z)
        self.changed_models[name] = True
        # self._calculate_model_matrix(name)
        # self._check_instance_update(name)

    # method to scale the mesh
    def scale(self, name, x, y, z):
        self.scales[name] = glm.vec3(x, y, z)
        self.changed_models[name] = True
        # self._calculate_model_matrix(name)
        # self._check_instance_update(name)

    def place_light(self, name, x, y, z):
        if name in self.lights:
            self.light_positions[self.lights[name] * 3 + 0] = x
            self.light_positions[self.lights[name] * 3 + 1] = y
            self.light_positions[self.lights[name] * 3 + 2] = z
        else:
            print_error(f"Light '{name}' not found")

    # method to calculate the model matrix after a transformation
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

    # method to check if an instance should be updated after a transformation
    def _check_instance_update(self, name):
        if self.models[name].in_instance == "":
            return
        
        for instance in self.instances.values():
            if self.models[name] in instance.models:
                instance.to_update["model_matrices"] = True
                instance.change_model_matrix(self.models[name], self.model_matrices[name])

    # ----------------------------- Modify Materials ---------------------------------

    def set_ambient(self, name, r, g, b):
        self.materials[name].set_ambient(r, g, b)
        self._check_instance_material_update(name, "ambients")

    def set_diffuse(self, name, r, g, b):
        self.materials[name].set_diffuse(r, g, b)
        self._check_instance_material_update(name, "diffuses")

    def set_specular(self, name, r, g, b):
        self.materials[name].set_specular(r, g, b)
        self._check_instance_material_update(name, "speculars")

    def set_shininess(self, name, s):
        self.materials[name].set_shininess(s)
        self._check_instance_material_update(name, "shininesses")

    def set_roughness(self, name, r):
        self.materials[name].set_roughness(r)
        self._check_instance_material_update(name, "roughnesses")

    def set_metallic(self, name, m):
        self.materials[name].set_metallic(m)
        self._check_instance_material_update(name, "metallicnesses")

    def set_light_color(self, name, r, g, b):
        if name in self.lights:
            self.light_colors[self.lights[name] * 3 + 0] = r
            self.light_colors[self.lights[name] * 3 + 1] = g
            self.light_colors[self.lights[name] * 3 + 2] = b
        else:
            print_error(f"Light '{name}' not found")

    def set_light_strength(self, name, s):
        if name in self.lights:
            self.light_strengths[self.lights[name]] = s
        else:
            print_error(f"Light '{name}' not found")

    def _check_instance_material_update(self, name, component):
        for model in self.materials[name].models:
            if model.in_instance != "":
                self.instances[model.in_instance].to_update[component] = True
                
                if component == "ambients":
                    self.instances[model.in_instance].change_ambient(self.materials[name])
                if component == "diffuses":
                    self.instances[model.in_instance].change_diffuse(self.materials[name])
                if component == "speculars":
                    self.instances[model.in_instance].change_specular(self.materials[name])
                if component == "shininesses":
                    self.instances[model.in_instance].change_shininess(self.materials[name])
                if component == "roughnesses":
                    self.instances[model.in_instance].change_roughness(self.materials[name])
                if component == "metallicnesses":
                    self.instances[model.in_instance].change_metallic(self.materials[name])

    # ---------------------------- Getters ------------------------------------------

    def light_material(self):
        return(self.materials["light_color"])

    # method to obtain an OpenGL ready matrix
    def get_ogl_matrix(self, name):
        return(glm.value_ptr(self.model_matrices[name]))

    def get_ogl_projection_matrix(self):
        return(glm.value_ptr(self.projection_matrix))

    # ------------------------------ Updaters ---------------------------------------

    # method to update the dimensions of the screen
    def update_dimensions(self, width, height):
        # update the internal dimensions
        self.width = int(width)
        self.height = int(height)

        self.projection_matrix = glm.perspective(glm.radians(self.fov), float(self.width)/float(self.height), 0.1, 10000.0)

        # bind the render framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self.render_framebuffer)

        # delete the renderbuffer and the texture of the framebuffer
        # glDeleteRenderbuffers(2, [self.depth_stencil_render_renderbuffer, self.blurred_depth_renderbuffer])
        glDeleteTextures(6, [self.multisample_render_texture, self.solved_texture, self.blurred_texture,
                             self.depth_texture, self.solved_depth_texture, self.blurred_depth_texture])

        # create a new color texture and depth/stencil renderbuffer with the updated dimensions
        self.multisample_render_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, self.multisample_render_texture)
        glTexImage2DMultisample(GL_TEXTURE_2D_MULTISAMPLE, self.max_samples, GL_RGB, self.width, self.height, GL_FALSE)
        # glTexImage2D(GL_TEXTURE_2D_MULTISAMPLE, 0, GL_RGB, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        # self.depth_stencil_render_renderbuffer = glGenRenderbuffers(1)
        # glBindRenderbuffer(GL_RENDERBUFFER, self.depth_stencil_render_renderbuffer)
        # glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, self.width, self.height)

        self.depth_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, self.depth_texture)
        # glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.width, self.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexImage2DMultisample(GL_TEXTURE_2D_MULTISAMPLE, self.max_samples, GL_DEPTH_COMPONENT, self.width, self.height, GL_FALSE)

        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # bind the new texture and renderbuffer to the framebuffer
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D_MULTISAMPLE, self.multisample_render_texture, 0)
        # glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, self.depth_stencil_render_renderbuffer)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D_MULTISAMPLE, self.depth_texture, 0)

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            error = glCheckFramebufferStatus(GL_FRAMEBUFFER)
            print("main framebuffer error")
            # print(glCheckFramebufferStatus(GL_FRAMEBUFFER))
            if error == GL_FRAMEBUFFER_UNDEFINED:
                print("GL_FRAMEBUFFER_UNDEFINED")
            if error == GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT:
                print("GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT")
            if error == GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT:
                print("GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT")
            if error == GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER:
                print("GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER")
            if error == GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER:
                print("GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER")
            if error == GL_FRAMEBUFFER_UNSUPPORTED:
                print("GL_FRAMEBUFFER_UNSUPPORTED")
            if error == GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE:
                print("GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE")
            if error == GL_FRAMEBUFFER_INCOMPLETE_LAYER_TARGETS:
                print("GL_FRAMEBUFFER_INCOMPLETE_LAYER_TARGETS")


        glBindFramebuffer(GL_FRAMEBUFFER, self.solved_framebuffer)
        self.solved_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.solved_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        self.solved_depth_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.solved_depth_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.width, self.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.solved_texture, 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.solved_depth_texture, 0)

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            print("framebuffer error")


        glBindFramebuffer(GL_FRAMEBUFFER, self.blurred_framebuffer)

        self.blurred_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.blurred_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        # self.blurred_depth_renderbuffer = glGenRenderbuffers(1)
        # glBindRenderbuffer(GL_RENDERBUFFER, self.blurred_depth_renderbuffer)
        # glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, self.width, self.height)

        self.blurred_depth_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.blurred_depth_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.width, self.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)


        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.blurred_texture, 0)
        # glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, self.blurred_depth_renderbuffer)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.blurred_depth_texture, 0)

        # self.depth_texture = glGenTextures(1)
        # glBindTexture(GL_TEXTURE_2D, self.depth_texture)
        # glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.width, self.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)


        # bind the default framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
                
    # update method to update components of the rendering manager
    def update(self):
        for model in self.changed_models:
            self._calculate_model_matrix(model)
            self._check_instance_update(model)

        self.changed_models = dict()

         # update the instances
        for instance in self.instances.values():
            instance.update()
          
    def recompile_shaders(self):
        for name, shader in self.shaders.items():
            glDeleteProgram(shader.program)
            shader.compile()


    # ------------------------------ Misc --------------------------------------------

    def add_post_processing_shader(self, name):
        self.post_processing_shaders.append(self.shaders[name])