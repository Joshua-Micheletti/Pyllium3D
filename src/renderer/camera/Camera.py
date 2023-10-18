import glm
import math

# class to implement a 3D virtual camera
class Camera:
    # constructor method
    def __init__(self):
        # postion vector
        self.position = glm.vec3(0.0, 0.0, 3.0)
        # direction vector
        self.front = glm.vec3(0.0, 0.0, -1.0)
        # world reference vector
        self.world_up = glm.vec3(0.0, 1.0, 0.0)

        # right vector, calculated based on the others
        self.right = glm.normalize(glm.cross(self.world_up, self.front))
        # up vector, calulated based on others
        self.up = glm.cross(self.front, self.right)

        # initialize the turn angles
        self.yaw = -90.0
        self.pitch = 0.0

        # calculate the view matrix
        self.view_matrix = glm.lookAt(self.position, self.position + self.front, self.world_up)

    # method to recalculate the vertices and view matrix
    def _calculate_vectors(self):
        self.right = glm.normalize(glm.cross(self.world_up, self.front))
        self.up = glm.cross(self.front, self.right)
        self.view_matrix = glm.lookAt(self.position, self.position + self.front, self.world_up)

    # method to move the camera forwards and backwards
    def move(self, amount):
        self.position += amount * self.front
        self._calculate_vectors()

    def place(self, x, y, z):
        self.position = glm.vec3(x, y, z)
        self._calculate_vectors()

    # method to strafe the camera left and right
    def strafe(self, amount):
        self.position += amount * self.right
        self._calculate_vectors()

    # method to lift the camera up and down
    def lift(self, amount):
        self.position += amount * self.world_up
        self._calculate_vectors()

    # method to turn the camera depending on the angle
    def turn(self, yaw, pitch):
        # add up the new orientation
        self.yaw += yaw
        self.pitch += pitch

        # clamp the pitch
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0

        # calculate the direction vector
        direction = glm.vec3(
            math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch)),
            math.sin(glm.radians(self.pitch)),
            math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        )

        # update the front vector
        self.front = glm.normalize(direction)
        # recalculate the rest of the vectors and view matrix
        self._calculate_vectors()

    # obtain a formatted version of the view matrix ready for opengl uniforms
    def get_ogl_matrix(self):
        return(glm.value_ptr(self.view_matrix))

    # def get_skybox_ogl_matrix(self):
    #     return(glm.value_ptr(glm.lookAt(glm.vec3(0), self.front, self.world_up)))