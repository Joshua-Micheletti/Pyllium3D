import multiprocessing
from threading import Thread

import glm


# function to create an indexed version of the vertices of a model
def index_vertices(vertices: list[float], normals: list[float], uvs: list[float]) -> tuple[list, list, list, list]:
    # dictionary to keep track of the non repeating vertices
    vertices_dict = {}

    # lists of indexed vertices to be returned
    out_vertices = []
    out_normals = []
    out_uvs = []
    out_indices = []

    # for each input vertex:
    for i in range(int(len(vertices) / 3)):
        # create a packed vertex (object that stores position, uv and normal information)
        packed_vertex = PackedVertex(
            position=glm.vec3(vertices[i * 3 + 0], vertices[i * 3 + 1], vertices[i * 3 + 2]),
            uv=glm.vec2(uvs[i * 2 + 0], uvs[i * 2 + 1]),
            normal=glm.vec3(normals[i * 3 + 0], normals[i * 3 + 1], normals[i * 3 + 2]),
        )

        # check if a similar vertex exists, if so, get its index
        found, index = get_similar_vertex_index(packed_vertex, vertices_dict)

        # if a similar vertex was found
        if found:
            # append its index to the indices list
            out_indices.append(index)
        # otherwise if it's a new vertex
        else:
            # store its values to the output lists
            out_vertices.append(vertices[i * 3 + 0])
            out_vertices.append(vertices[i * 3 + 1])
            out_vertices.append(vertices[i * 3 + 2])

            out_uvs.append(uvs[i * 2 + 0])
            out_uvs.append(uvs[i * 2 + 1])

            out_normals.append(normals[i * 3 + 0])
            out_normals.append(normals[i * 3 + 1])
            out_normals.append(normals[i * 3 + 2])

            # calculate the index of the last item (new)
            new_index = int(len(out_vertices) / 3 - 1)
            # append the new index in the output list of indices
            out_indices.append(new_index)

            # store the packed vertex in the dictionary
            vertices_dict[packed_vertex] = new_index

    # return the output lists
    return (out_indices, out_vertices, out_normals, out_uvs)


def index_vertices_st_worker(
    vertices: list[float], normals: list[float], uvs: list[float], procnum: bool, return_dict: dict
) -> None:
    return_dict[procnum] = index_vertices(vertices, normals, uvs)


def index_vertices_multi_thread(
    vertices: list[float], normals: list[float], uvs: list[float]
) -> tuple[list, list, list, list]:
    thread_count = multiprocessing.cpu_count()
    # thread_count = 30
    vertex_length = int(len(vertices) / thread_count)
    vertex_length -= vertex_length % 3
    uv_length = int(len(uvs) / thread_count)
    uv_length -= uv_length % 2

    out_vertices = []
    out_normals = []
    out_uvs = []

    i = 0

    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    threads = []
    for i in range(thread_count):
        # if i == thread_count - 1:
        #     thread_vertices = [vertices[index] for index in range(i*vertex_length, len(vertices))]
        #     thread_normals = [normals[index] for index in range(i*vertex_length, len(normals))]
        #     thread_uvs = [uvs[index] for index in range(i*uv_length, len(uvs))]

        # else:
        thread_vertices = [vertices[index] for index in range(i * vertex_length, i * vertex_length + vertex_length)]
        thread_normals = [normals[index] for index in range(i * vertex_length, i * vertex_length + vertex_length)]
        thread_uvs = [uvs[index] for index in range(i * uv_length, i * uv_length + uv_length)]

        print(f'normals thread size: {len(thread_normals)}')

        p = multiprocessing.Process(
            target=index_vertices_st_worker,
            args=(thread_vertices, thread_normals, thread_uvs, i, return_dict),
        )
        threads.append(p)
        p.start()

    for thread in threads:
        thread.join()

    for result in return_dict.values():
        out_vertices += result[1]
        out_normals += result[2]
        out_uvs += result[3]

    print(f'len reduced vertices: {len(out_vertices)}')
    print(f'len reduced normals: {len(out_normals)}')
    print(f'len reduced uvs: {len(out_uvs)}')

    return index_vertices(out_vertices, out_normals, out_uvs)


# function to check wether a packed vertex is similar to any vertex in the dictionary (==)
def get_similar_vertex_index(packed: 'PackedVertex', vertices: list['PackedVertex']) -> tuple[bool, int]:
    # for every vertex in the dictionary
    for vertex, index in vertices.items():
        # check if it's similar to the current packed vertex
        if vertex == packed:
            # if a similar vertex is found, return True and the index it was found at
            return (True, index)

    # if no vertex in the dictionary is similar, return False
    return (False, None)


# class to store and compare packed vertices
class PackedVertex:
    # constructor method
    def __init__(self, position: list[float], uv: list[float], normal: list[float]) -> None:
        # store the passed information
        self.position = position
        self.uv = uv
        self.normal = normal

    # method to execute when the "==" operator is used
    def __eq__(self, other: any) -> bool:
        """Define the equality criteria.

        Args:
            other (Obj): object to compare to

        Returns:
            boolean: true or false depending if the objects match

        """
        # return true if the fields are the same
        return self.__dict__ == other.__dict__
        # return(self.position.x == other.position.x and \
        #        self.position.y == other.position.y and \
        #        self.position.z == other.position.z and \
        #        self.uv.x == other.uv.x and
        #        self.uv.y == other.uv.y and
        #        self.normal.x == other.normal.x and
        #        self.normal.y == other.normal.y and
        #        self.normal.z == other.normal.z)
        # return(self.is_near(self.position.x, other.position.x) and \
        #        self.is_near(self.position.y, other.position.y) and \
        #        self.is_near(self.position.z, other.position.z) and \
        #        self.is_near(self.uv.x, other.uv.x) and
        #        self.is_near(self.uv.y, other.uv.y) and
        #        self.is_near(self.normal.x, other.normal.x) and
        #        self.is_near(self.normal.y, other.normal.y) and
        #        self.is_near(self.normal.z, other.normal.z))

    # redefine the hashing function
    def __hash__(self) -> int:
        """Hashing.

        Returns:
            str: unique identifier of the object

        """
        return hash(self.__dict__.values())

    # method to check if a value can be considered near enough to another value
    def is_near(self, v1: float, v2: float) -> bool:
        """Check if the vertices are close to each other.

        Args:
            v1: Vertex 1
            v2: Vertex 2

        Returns:
            boolean: true or false depending if the vertices are close enough to each other

        """
        return abs(v1 - v2) < 0.001


class IndexingThread(Thread):
    """Class for creating indexing threads.

    Args:
        Thread: Class to inherit to be a thread

    """

    def __init__(self, vertices: list[float], normals: list[float], uvs: list[float]) -> None:
        """Initialize the thread.

        Args:
            vertices (dict): dictionary of vertices
            normals (dict): dictionary of normals
            uvs (dict): dictionary of UVs

        """
        Thread.__init__(self)
        self.vertices = vertices
        self.normals = normals
        self.uvs = uvs

        self._return = None

    def run(self) -> None:
        """Thread logic function.

        Returns:
            tuple: output data

        """
        # dictionary to keep track of the non repeating vertices
        vertices_dict = {}

        # lists of indexed vertices to be returned
        out_vertices = []
        out_normals = []
        out_uvs = []
        out_indices = []

        # for each input vertex:
        for i in range(int(len(self.vertices) / 3)):
            # create a packed vertex (object that stores position, uv and normal information)
            packed_vertex = PackedVertex(
                position=glm.vec3(
                    self.vertices[i * 3 + 0],
                    self.vertices[i * 3 + 1],
                    self.vertices[i * 3 + 2],
                ),
                uv=glm.vec2(self.uvs[i * 2 + 0], self.uvs[i * 2 + 1]),
                normal=glm.vec3(
                    self.normals[i * 3 + 0],
                    self.normals[i * 3 + 1],
                    self.normals[i * 3 + 2],
                ),
            )

            # check if a similar vertex exists, if so, get its index
            found, index = get_similar_vertex_index(packed_vertex, vertices_dict)

            # if a similar vertex was found
            if found:
                # append its index to the indices list
                out_indices.append(index)
            # otherwise if it's a new vertex
            else:
                # store its values to the output lists
                out_vertices.append(self.vertices[i * 3 + 0])
                out_vertices.append(self.vertices[i * 3 + 1])
                out_vertices.append(self.vertices[i * 3 + 2])

                out_uvs.append(self.uvs[i * 2 + 0])
                out_uvs.append(self.uvs[i * 2 + 1])

                out_normals.append(self.normals[i * 3 + 0])
                out_normals.append(self.normals[i * 3 + 1])
                out_normals.append(self.normals[i * 3 + 2])

                # calculate the index of the last item (new)
                new_index = int(len(out_vertices) / 3 - 1)
                # append the new index in the output list of indices
                out_indices.append(new_index)

                # store the packed vertex in the dictionary
                vertices_dict[packed_vertex] = new_index

        # return the output lists
        self._return = (out_indices, out_vertices, out_normals, out_uvs)
