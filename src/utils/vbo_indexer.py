import glm

# function to create an indexed version of the vertices of a model
def index_vertices(vertices, normals, uvs):
    # dictionary to keep track of the non repeating vertices
    vertices_dict = dict()

    # lists of indexed vertices to be returned
    out_vertices = []
    out_normals = []
    out_uvs = []
    out_indices = []

    # for each input vertex:
    for i in range(int(len(vertices) / 3)):
        # create a packed vertex (object that stores position, uv and normal information)
        packed_vertex = PackedVertex(position=glm.vec3(vertices[i * 3 + 0], vertices[i * 3 + 1], vertices[i * 3 + 2]),
                                     uv = glm.vec2(uvs[i * 2 + 0], uvs[i * 2 + 1]),
                                     normal = glm.vec3(normals[i * 3 + 0], normals[i * 3 + 1], normals[i * 3 + 2]))
        
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
    return(out_indices, out_vertices, out_normals, out_uvs)

# function to check wether a packed vertex is similar to any vertex in the dictionary (==)
def get_similar_vertex_index(packed, vertices):
    # for every vertex in the dictionary
    for vertex, index in vertices.items():
        # check if it's similar to the current packed vertex
        if vertex == packed:
            # if a similar vertex is found, return True and the index it was found at
            return(True, index)

    # if no vertex in the dictionary is similar, return False    
    return(False, None)


# class to store and compare packed vertices
class PackedVertex:
    # constructor method
    def __init__(self, position, uv, normal):
        # store the passed information
        self.position = position
        self.uv = uv
        self.normal = normal

    # method to execute when the "==" operator is used
    def __eq__(self, other):
        # return true if the fields are the same
        return(self.__dict__ == other.__dict__)
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
    def __hash__(self):
        return hash(self.__dict__.values())

    # method to check if a value can be considered near enough to another value
    def is_near(self, v1, v2):
        return(abs(v1 - v2) < 0.001)