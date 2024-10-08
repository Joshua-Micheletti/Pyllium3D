# ruff: noqa: F403, F405

import json

import glm
import numpy as np
import pywavefront
from OpenGL.GL import *

from utils import *


class MeshManager(metaclass=Singleton):
    def __init__(self):
        # dictionaries of OpenGL VBOs for vertex data (vertex, normal, uv)
        self._vertex_vbos: dict[str, int] = {}
        self._normal_vbos: dict[str, int] = {}
        self._uv_vbos: dict[str, int] = {}
        # dictionary of OpenGL EBOs for index data
        self._ebos: dict[str, int] = {}
        # dictionary of OpenGL VAO for vertex data
        self._vaos: dict[str, int] = {}
        # dictionary of number of vertices per mesh
        self._vertices_count: dict[str, int] = {}
        # dictionary of number of indices per mesh
        self._indices_count: dict[str, int] = {}

        # bounding box and sphere data
        self._aabb_mins: dict[str, glm.vec3] = {}
        self._aabb_maxs: dict[str, glm.vec3] = {}

        self._bounding_sphere_radius: dict[str, float] = {}
        self._bounding_sphere_center: dict[str, glm.vec3] = {}

        self._indices: dict[str, int] = {}

    def vao(self, name: str) -> int:
        return self._vaos.get(name)

    def new_mesh(self, name: str, file_path: str) -> None:
        # empty lists to contain the vertices data taken from the file
        formatted_vertices = []
        formatted_normals = []
        formatted_uvs = []

        # load the mesh from the file path
        scene = pywavefront.Wavefront(file_path, collect_faces=True)

        # iterate through all the meshes in the file
        for _, material in scene.materials.items():
            # scroll through the vertices data by increments of 8 (u, v, n.x, n.y, n.z, v.x, v.y, v.z)
            for i in range(0, len(material.vertices), 8):
                # u
                formatted_uvs.append(material.vertices[i])
                # v
                formatted_uvs.append(material.vertices[i + 1])

                # n.x
                formatted_normals.append(material.vertices[i + 2])
                # n.y
                formatted_normals.append(material.vertices[i + 3])
                # n.z
                formatted_normals.append(material.vertices[i + 4])

                # v.x
                formatted_vertices.append(material.vertices[i + 5])
                # v.y
                formatted_vertices.append(material.vertices[i + 6])
                # v.z
                formatted_vertices.append(material.vertices[i + 7])

        # format the lists into np.arrays of type float 32bit
        formatted_vertices = np.array(formatted_vertices, dtype=np.float32)
        formatted_normals = np.array(formatted_normals, dtype=np.float32)
        formatted_uvs = np.array(formatted_uvs, dtype=np.float32)

        # convert the lists into indiced lists and obtain an indices list for indexed rendering
        indices, indiced_vertices, indiced_normals, indiced_uvs = index_vertices(
            formatted_vertices, formatted_normals, formatted_uvs
        )

        # keep track of the indices count
        self._indices_count[name] = len(indices)

        # convert the indexed lists into indexed arrays of type float 32bit
        indiced_vertices = np.array(indiced_vertices, dtype=np.float32)
        indiced_normals = np.array(indiced_normals, dtype=np.float32)
        indiced_uvs = np.array(indiced_uvs, dtype=np.float32)

        # convert the list of indices into an array of indices of type unsigned int 32bit
        indices = np.array(indices, dtype=np.uint32)

        # generate the OpenGL buffers (VBO) for each data type
        self._vertex_vbos[name] = glGenBuffers(1)
        self._normal_vbos[name] = glGenBuffers(1)
        self._uv_vbos[name] = glGenBuffers(1)
        self._ebos[name] = glGenBuffers(1)
        # generate the OpenGL buffer (VAO) to store all the data
        self._vaos[name] = glGenVertexArrays(1)

        # store the vertices count
        self._vertices_count[name] = len(formatted_vertices) / 3

        # bind the VAO
        glBindVertexArray(self._vaos[name])

        # bind the vertex VBO
        glBindBuffer(GL_ARRAY_BUFFER, self._vertex_vbos[name])
        # store the data into the VBO
        glBufferData(GL_ARRAY_BUFFER, indiced_vertices.nbytes, indiced_vertices, GL_STATIC_DRAW)
        # enable the index 0 of the VAO
        glEnableVertexAttribArray(0)
        # store the data from the VBO in the VAO
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        # repeat for normals
        glBindBuffer(GL_ARRAY_BUFFER, self._normal_vbos[name])
        glBufferData(GL_ARRAY_BUFFER, indiced_normals.nbytes, indiced_normals, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        # and UVs
        glBindBuffer(GL_ARRAY_BUFFER, self._uv_vbos[name])
        glBufferData(GL_ARRAY_BUFFER, indiced_uvs.nbytes, indiced_uvs, GL_STATIC_DRAW)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        # pass the data for the element array buffer of indices
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._ebos[name])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    def new_json_mesh(self, name: str, file_path: str) -> None:
        # open the json model
        with open(file_path) as f:
            data = json.load(f)

        # keep track of the indices count
        self._indices_count[name] = len(data['indices'])

        # convert the indexed lists into indexed arrays of type float 32bit
        indiced_vertices = np.array(data['vertices'], dtype=np.float32)
        indiced_normals = np.array(data['normals'], dtype=np.float32)
        indiced_uvs = np.array(data['uvs'], dtype=np.float32)

        # convert the list of indices into an array of indices of type unsigned int 32bit
        indices = np.array(data['indices'], dtype=np.uint32)

        # generate the OpenGL buffers (VBO) for each data type
        self._vertex_vbos[name] = glGenBuffers(1)
        self._normal_vbos[name] = glGenBuffers(1)
        self._uv_vbos[name] = glGenBuffers(1)
        self._ebos[name] = glGenBuffers(1)
        # generate the OpenGL buffer (VAO) to store all the data
        self._vaos[name] = glGenVertexArrays(1)

        # store the vertices count
        self._vertices_count[name] = len(indiced_vertices) / 3

        # bind the VAO
        glBindVertexArray(self._vaos[name])

        # bind the vertex VBO
        glBindBuffer(GL_ARRAY_BUFFER, self._vertex_vbos[name])
        # store the data into the VBO
        glBufferData(GL_ARRAY_BUFFER, indiced_vertices.nbytes, indiced_vertices, GL_STATIC_DRAW)
        # enable the index 0 of the VAO
        glEnableVertexAttribArray(0)
        # store the data from the VBO in the VAO
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        # repeat for normals
        glBindBuffer(GL_ARRAY_BUFFER, self._normal_vbos[name])
        glBufferData(GL_ARRAY_BUFFER, indiced_normals.nbytes, indiced_normals, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        # and UVs
        glBindBuffer(GL_ARRAY_BUFFER, self._uv_vbos[name])
        glBufferData(GL_ARRAY_BUFFER, indiced_uvs.nbytes, indiced_uvs, GL_STATIC_DRAW)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        # pass the data for the element array buffer of indices
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._ebos[name])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        center = data['center']
        max_distance = data['max_distance']

        self._aabb_mins[name] = center - glm.vec3(max_distance)
        self._aabb_maxs[name] = center + glm.vec3(max_distance)

        self._bounding_sphere_radius[name] = max_distance
        self._bounding_sphere_center[name] = center

    def bind_mesh(self, name: str) -> int:
        glBindVertexArray(self._vaos.get(name))
        return self._indices_count.get(name)
