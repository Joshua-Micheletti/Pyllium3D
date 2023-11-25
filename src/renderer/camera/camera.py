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

        self.frustum = Frustum()

        # calculate the view matrix
        self.view_matrix = glm.lookAt(self.position, self.position + self.front, self.world_up)

    def set_frustum_params(self, aspect, fov_y, z_near, z_far):
        self.aspect = aspect
        self.fov_y = fov_y
        self.z_near = z_near
        self.z_far = z_far

    # method to recalculate the vertices and view matrix
    def _calculate_vectors(self):
        self.right = glm.normalize(glm.cross(self.world_up, self.front))
        self.up = glm.cross(self.front, self.right)
        self.view_matrix = glm.lookAt(self.position, self.position + self.front, self.world_up)

        self._calculate_frustum()

    def _calculate_frustum(self):
        half_v_side = self.z_far * math.tan(self.fov_y * 0.5)
        half_h_side = half_v_side * self.aspect

        front_mult_far = self.z_far * self.front

        self.frustum.near = Plane(self.position + self.z_near * self.front, self.front)
        self.frustum.far  = Plane(self.position + front_mult_far, -self.front)
        self.frustum.right = Plane(self.position, glm.cross(front_mult_far - self.right * half_h_side, self.up))
        self.frustum.left = Plane(self.position, glm.cross(self.up, front_mult_far + self.right * half_h_side))
        self.frustum.top = Plane(self.position, glm.cross(self.right, front_mult_far - self.up * half_v_side))
        self.frustum.bottom = Plane(self.position, glm.cross(front_mult_far + self.up * half_v_side, self.right))

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

class Plane:
    # def __init__(self, distance = 0.0, normal_x = 0.0, normal_y = 1.0, normal_z = 0.0):
    #     self.normal = glm.vec3(normal_x, normal_y, normal_z)
    #     self.distance = distance

    def __init__(self, p1, normal):
        self.normal = normal
        self.distance = glm.dot(normal, p1)

class Frustum:
    def __init__(self):
        self.top = None
        self.bottom = None
        self.right = None
        self.left = None
        self.far = None
        self.near = None