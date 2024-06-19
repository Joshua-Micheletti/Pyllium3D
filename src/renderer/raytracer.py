from ctypes import c_void_p

import numpy as np
from pyrr import Matrix44
from utils import Singleton
from OpenGL.GL import *
from renderer.renderer_manager import RendererManager
import time
from icecream import ic


class RayTracer(metaclass=Singleton):
    """RayTracer engine"""

    def __init__(self):
        # set the color to clear the screen with
        glClearColor(0.1, 0.1, 0.1, 1.0)
        # enable alpha blending
        glEnable(GL_BLEND)
        # define the blending function
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # vertices for the screen rendering
        vertices = [
            -1.0,
            1.0,
            0.0,
            0.0,
            1.0,
            -1.0,
            -1.0,
            0.0,
            0.0,
            0.0,
            1.0,
            1.0,
            0.0,
            1.0,
            1.0,
            1.0,
            -1.0,
            0.0,
            1.0,
            0.0,
        ]

        # convert the vertices in GLfloat
        vertices = (GLfloat * len(vertices))(*vertices)

        # OGL Vertex Buffer Object (to store the vertices)
        self.vbo = None
        # OGL Vertex Array Object (to pass the vertices to the GPU)
        self.vao = None

        # generate the VAO and the VBO
        self.vao = glGenVertexArrays(1, self.vao)
        self.vbo = glGenBuffers(1, self.vbo)
        # bind the VAO and the VBO
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        # pass the vertices data to the VBO
        glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW)
        # bind the VAO point 0 to the first 3 values of the VBO (vertices)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(
            0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), c_void_p(0)
        )
        # bind the VAO point 1 to the last 2 values of the VBO (UVs)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(
            1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), c_void_p(3 * sizeof(GLfloat))
        )

        # generate a buffer for each thing required in the raytracer
        self.vertices = glGenBuffers(1)
        self.model_mats = glGenBuffers(1)
        self.indices = glGenBuffers(1)
        self.normals = glGenBuffers(1)
        self.spheres = glGenBuffers(1)
        self.planes = glGenBuffers(1)
        self.boxes = glGenBuffers(1)
        self.bounding_boxes = glGenBuffers(1)
        self.materials = glGenBuffers(1)
        self.mesh_material_indices = glGenBuffers(1)

        # renderer size
        self.render_x = 1280
        self.render_y = 720

        # get a reference to the camera (need to bind to my camera object)
        # self.camera = Camera.getInstance()

        # i'm guessing this is a counter for rendering time
        self.render_time = 0

        # # no idea
        # self.light_index = 2
        # # model matrix for the light source ?
        # self.light_model = Matrix44.identity()

        # MAKE MY CODE SUPPORT COMPUTE SHADERS
        # extract the content of the shader file
        compute_shader_source = ""
        # create the compute shader
        self.compute_shader = glCreateShader(GL_COMPUTE_SHADER)
        # read the content of the compute shader
        text = open("assets/shaders/raytracing/compute.glsl", "r")
        compute_shader_source = text.read()

        # bind the source of the shader to the shader object
        glShaderSource(self.compute_shader, compute_shader_source)
        # compile the code
        glCompileShader(self.compute_shader)

        # check for compilation errors
        status = None
        glGetShaderiv(self.compute_shader, GL_COMPILE_STATUS, status)
        if status == GL_FALSE:
            # Note that getting the error log is much simpler in Python than in C/C++
            # and does not require explicit handling of the string buffer
            strInfoLog = glGetShaderInfoLog(self.compute_shader)
            strShaderType = "compute"

            print(
                "Compilation failure for " + strShaderType + " shader:\n" + strInfoLog
            )

        # create the program object and bind it as the main rendering object
        self.program_id = glCreateProgram()
        glAttachShader(self.program_id, self.compute_shader)
        glLinkProgram(self.program_id)
        print(glGetProgramInfoLog(self.program_id))

        # create the screen texture
        self.texture = 0
        self.texture = glGenTextures(1, self.texture)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexStorage2D(GL_TEXTURE_2D, 1, GL_RGBA32F, self.render_x, self.render_y)
        glBindImageTexture(0, self.texture, 1, GL_TRUE, 0, GL_READ_WRITE, GL_RGBA32F)

        # create a texture for the last frame (accumulation)
        self.last_frame = 0
        self.last_frame = glGenTextures(1, self.last_frame)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.last_frame)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexStorage2D(GL_TEXTURE_2D, 1, GL_RGBA32F, self.render_x, self.render_y)
        glBindImageTexture(0, self.last_frame, 1, GL_TRUE, 0, GL_READ_WRITE, GL_RGBA32F)

        # create a shader for showing the result on the screen
        # self.screen_shader = Shader("../shaders/screen_vertex.glsl", "../shaders/screen_fragment.glsl")

        # counter of how many frames have been rendered, used for accumulation
        self.rendered_frames = 0

        self.bounces = 2

        self.denoise = 0
        self.far_plane = 1.0

        # self.load_material(1, 1, 1, 1, 1, 1, 10, 1, 1, 1, 1, 1)
        # self.load_sphere(1, 1, 1, 1, 0)

        self.update_materials(np.array([1, 1, 1, 1, 1, 1, 10, 1, 1, 1, 1, 1]))
        self.update_spheres(np.array([1, 1, 1, 1, 0]))
        self.update_planes(np.array([0, 0, 0, 0, 1, 0, 0]))

    def render(self):
        rm = RendererManager()
        # set the active texture slot to 0
        glActiveTexture(GL_TEXTURE0)
        # bind the screen texture to that slot
        glBindTexture(GL_TEXTURE_2D, self.texture)
        # bind the image to that texture
        glBindImageTexture(0, self.texture, 0, GL_FALSE, 0, GL_READ_WRITE, GL_RGBA32F)

        # use the compute shader
        glUseProgram(self.program_id)

        # get the inverse view projection matrix from the camera
        # glUniformMatrix4fv(
        #     glGetUniformLocation(self.program_id, "inverse_view_projection"),
        #     1,
        #     GL_FALSE,
        #     rm.get_ogl_inv_view_proj_matrix(),
        # )
        glUniformMatrix4fv(
            glGetUniformLocation(self.program_id, "inverse_view_projection"),
            1,
            GL_FALSE,
            rm.get_ogl_inv_view_proj_matrix(),
        )

        # get the camera position
        glUniform3f(
            glGetUniformLocation(self.program_id, "eye"),
            rm.camera.position[0],
            rm.camera.position[1],
            rm.camera.position[2],
        )
        # get the time to the shader
        glUniform1f(
            glGetUniformLocation(self.program_id, "time"), float(time.time() % 1)
        )
        # get the number of bounces to the shader
        glUniform1f(
            glGetUniformLocation(self.program_id, "bounces"), float(self.bounces)
        )

        # dispatch the compute workers depending on the size of the screen
        glDispatchCompute(int(self.render_x / 8), int(self.render_y / 4), 1)
        glMemoryBarrier(GL_ALL_BARRIER_BITS)

        # clear the buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # use the screen shader
        # glUseProgram(self.screen_shader.program)
        screen_shader = rm.shaders.get("raytracing_screen")

        screen_shader.use()

        # glBindFramebuffer(GL_FRAMEBUFFER, rm.solved_framebuffer)

        # pass the required textures
        glUniform1i(glGetUniformLocation(screen_shader.program, "tex"), 0)
        glUniform1i(glGetUniformLocation(screen_shader.program, "old_tex"), 1)
        glUniform1f(
            glGetUniformLocation(screen_shader.program, "frames"), self.rendered_frames
        )
        glUniform1f(
            glGetUniformLocation(screen_shader.program, "denoise"), self.denoise
        )

        glBindVertexArray(self.vao)

        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
        glBindVertexArray(0)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        if self.denoise != 0:
            self.rendered_frames += 1
            glBindTexture(GL_TEXTURE_2D, self.last_frame)
            glCopyTexSubImage2D(
                GL_TEXTURE_2D, 0, 0, 0, 0, 0, self.render_x, self.render_y
            )

    def update_mesh_material_indices(self, mesh_mat_i):
        data = (GLfloat * len(mesh_mat_i))(*mesh_mat_i)

        glBindBuffer(GL_UNIFORM_BUFFER, self.mesh_material_indices)
        glBufferData(GL_UNIFORM_BUFFER, sizeof(data), data, GL_STATIC_DRAW)
        glBindBufferBase(GL_UNIFORM_BUFFER, 10, self.mesh_material_indices)
        glBindBuffer(GL_UNIFORM_BUFFER, 0)

    def update_vertices(self, vertices):
        data = (GLfloat * len(vertices))(*vertices)

        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.vertices)
        glBufferData(GL_SHADER_STORAGE_BUFFER, sizeof(data), data, GL_STATIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, self.vertices)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)

    def update_indices(self, indices):
        data = (GLfloat * len(indices))(*indices)

        glBindBuffer(GL_UNIFORM_BUFFER, self.indices)
        glBufferData(GL_UNIFORM_BUFFER, sizeof(data), data, GL_STATIC_DRAW)
        glBindBufferBase(GL_UNIFORM_BUFFER, 3, self.indices)
        glBindBuffer(GL_UNIFORM_BUFFER, 0)

    def update_model_mats(self, model_mats):
        data = (GLfloat * len(model_mats))(*model_mats)

        glBindBuffer(GL_UNIFORM_BUFFER, self.model_mats)
        glBufferData(GL_UNIFORM_BUFFER, sizeof(data), data, GL_STATIC_DRAW)
        glBindBufferBase(GL_UNIFORM_BUFFER, 2, self.model_mats)
        glBindBuffer(GL_UNIFORM_BUFFER, 0)

    def update_normals(self, normals):
        data = (GLfloat * len(normals))(*normals)

        glBindBuffer(GL_UNIFORM_BUFFER, self.normals)
        glBufferData(GL_UNIFORM_BUFFER, sizeof(data), data, GL_STATIC_DRAW)
        glBindBufferBase(GL_UNIFORM_BUFFER, 4, self.normals)
        glBindBuffer(GL_UNIFORM_BUFFER, 0)

    def update_spheres(self, spheres):
        data = (GLfloat * len(spheres))(*spheres)

        glBindBuffer(GL_UNIFORM_BUFFER, self.spheres)
        glBufferData(GL_UNIFORM_BUFFER, sizeof(data), data, GL_STATIC_DRAW)
        glBindBufferBase(GL_UNIFORM_BUFFER, 5, self.spheres)
        glBindBuffer(GL_UNIFORM_BUFFER, 0)

    def update_planes(self, planes):
        data = (GLfloat * len(planes))(*planes)

        glBindBuffer(GL_UNIFORM_BUFFER, self.planes)
        glBufferData(GL_UNIFORM_BUFFER, sizeof(data), data, GL_STATIC_DRAW)
        glBindBufferBase(GL_UNIFORM_BUFFER, 6, self.planes)
        glBindBuffer(GL_UNIFORM_BUFFER, 0)

    def update_boxes(self, boxes):
        data = (GLfloat * len(boxes))(*boxes)

        glBindBuffer(GL_UNIFORM_BUFFER, self.boxes)
        glBufferData(GL_UNIFORM_BUFFER, sizeof(data), data, GL_STATIC_DRAW)
        glBindBufferBase(GL_UNIFORM_BUFFER, 7, self.boxes)
        glBindBuffer(GL_UNIFORM_BUFFER, 0)

    def update_bounding_boxes(self, bounding_boxes):
        # print(bounding_boxes)
        data = (GLfloat * len(bounding_boxes))(*bounding_boxes)

        glBindBuffer(GL_UNIFORM_BUFFER, self.bounding_boxes)
        glBufferData(GL_UNIFORM_BUFFER, sizeof(data), data, GL_STATIC_DRAW)
        glBindBufferBase(GL_UNIFORM_BUFFER, 8, self.bounding_boxes)
        glBindBuffer(GL_UNIFORM_BUFFER, 0)

    def update_materials(self, materials):
        data = (GLfloat * len(materials))(*materials)

        glBindBuffer(GL_UNIFORM_BUFFER, self.materials)
        glBufferData(GL_UNIFORM_BUFFER, sizeof(data), data, GL_STATIC_DRAW)
        glBindBufferBase(GL_UNIFORM_BUFFER, 9, self.materials)
        glBindBuffer(GL_UNIFORM_BUFFER, 0)
