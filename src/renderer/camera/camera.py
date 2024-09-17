import math

import glm


# class to implement a 3D virtual camera
class Camera:
    # constructor method
    def __init__(self) -> None:
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

    def set_frustum_params(self, aspect, fov_y, z_near, z_far) -> None:
        self.aspect = aspect
        self.fov_y = fov_y
        self.z_near = z_near
        self.z_far = z_far

    # method to recalculate the vertices and view matrix
    def _calculate_vectors(self) -> None:
        self.right = glm.normalize(glm.cross(self.world_up, self.front))
        self.up = glm.cross(self.front, self.right)
        self.view_matrix = glm.lookAt(self.position, self.position + self.front, self.world_up)

        self._calculate_frustum()

    def _calculate_frustum(self) -> None:
        half_v_side = self.z_far * math.tan(self.fov_y * 0.5)
        # print(half_v_side)
        # half_v_side = self.z_far * float(math.tan(self.fov_y * 0.5))
        # half_v_side = self.z_far * self.fov_y

        half_h_side = half_v_side * self.aspect

        front_mult_far = self.z_far * self.front

        self.frustum.near = Plane(self.position + self.z_near * self.front, self.front)

        self.frustum.far = Plane(self.position + front_mult_far, -self.front)

        self.frustum.right = Plane(self.position, glm.cross(front_mult_far + self.right * half_h_side, self.up))

        self.frustum.left = Plane(self.position, glm.cross(self.up, front_mult_far - self.right * half_h_side))

        self.frustum.top = Plane(self.position, glm.cross(self.right, front_mult_far + self.up * half_v_side))

        self.frustum.bottom = Plane(self.position, glm.cross(front_mult_far - self.up * half_v_side, self.right))

    # method to move the camera forwards and backwards
    def move(self, amount) -> None:
        self.position += amount * self.front
        self._calculate_vectors()

    def place(self, x, y, z) -> None:
        self.position = glm.vec3(x, y, z)
        self._calculate_vectors()

    # method to strafe the camera left and right
    def strafe(self, amount) -> None:
        self.position += amount * self.right
        self._calculate_vectors()

    # method to lift the camera up and down
    def lift(self, amount) -> None:
        self.position += amount * self.world_up
        self._calculate_vectors()

    # method to turn the camera depending on the angle
    def turn(self, yaw, pitch) -> None:
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
            math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch)),
        )

        # update the front vector
        self.front = glm.normalize(direction)
        # recalculate the rest of the vectors and view matrix
        self._calculate_vectors()

    # obtain a formatted version of the view matrix ready for opengl uniforms
    def get_ogl_matrix(self):
        return glm.value_ptr(self.view_matrix)

    # def get_inv_view_proj_matrix(self):
    #     view_projection_matrix = self.projection_matrix * self.get_view_matrix()

    # def get_skybox_ogl_matrix(self):
    #     return(glm.value_ptr(glm.lookAt(glm.vec3(0), self.front, self.world_up)))


class Plane:
    def __init__(self, p1, normal) -> None:
        self.normal = glm.normalize(normal)

        if isinstance(p1, glm.vec3):
            # self.normal = glm.normalize(normal)
            self.point = p1
            # self.distance = abs(glm.dot(normal, p1))
            self.distance = glm.dot(self.normal, p1)
        elif isinstance(p1, float):
            self.distance = p1

    # def __init__(self, distance: float, normal: glm.vec3):
    #     self.normal = glm.normalize(normal)
    #     self.distance = distance

    # def set_normal(self, normal):
    #     self.normal = glm.normalize(normal)


class Frustum:
    def __init__(self) -> None:
        self.top = None
        self.bottom = None
        self.right = None
        self.left = None
        self.far = None
        self.near = None

    def __str__(self) -> str:
        string = ''

        if self.near is not None:
            string += (
                'Near:  \n Normal: '
                + str(self.near.normal)
                + '\n Distance: '
                + str(self.near.distance)
                + '\n Center: '
                + str(self.near.point)
                + '\n'
            )
        if self.far is not None:
            string += (
                'Far:   \n Normal: '
                + str(self.far.normal)
                + '\n Distance: '
                + str(self.far.distance)
                + '\n Center: '
                + str(self.far.point)
                + '\n'
            )
        if self.right is not None:
            string += (
                'Right: \n Normal: '
                + str(self.right.normal)
                + '\n Distance: '
                + str(self.right.distance)
                + '\n Center: '
                + str(self.right.point)
                + '\n'
            )
        if self.left is not None:
            string += (
                'Left:  \n Normal: '
                + str(self.left.normal)
                + '\n Distance: '
                + str(self.left.distance)
                + '\n Center: '
                + str(self.left.point)
                + '\n'
            )
        if self.top is not None:
            string += (
                'Top:   \n Normal: '
                + str(self.top.normal)
                + '\n Distance: '
                + str(self.top.distance)
                + '\n Center: '
                + str(self.top.point)
                + '\n'
            )
        if self.bottom is not None:
            string += (
                'Bottom:\n Normal: '
                + str(self.bottom.normal)
                + '\n Distance: '
                + str(self.bottom.distance)
                + '\n Center: '
                + str(self.bottom.point)
                + '\n'
            )

        return string
