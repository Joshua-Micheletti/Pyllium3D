"""Frustum Module."""

import math

import glm

from renderer.camera.frustum.plane import Plane


class Frustum:
    """Implement a 3D Frustum."""

    # ------------------------------- Magic methods ------------------------------ #
    def __init__(
        self,
        position: glm.vec3 = None,
        front: glm.vec3 = None,
        right: glm.vec3 = None,
        up: glm.vec3 = None,
        fov_y: float = 60.0,
        z_near: float = 0.1,
        z_far: float = 10000.0,
        aspect: float = 1,
    ) -> None:
        """Create the Frustum.

        Args:
            position (glm.vec3, optional): Position vector. Defaults to None.
            front (glm.vec3, optional): Front vector. Defaults to None.
            right (glm.vec3, optional): Right vector. Defaults to None.
            up (glm.vec3, optional): Up vector. Defaults to None.
            fov_y (float, optional): Vertical field of view. Defaults to 60.0.
            z_near (float, optional): Z Near distance. Defaults to 0.1.
            z_far (float, optional): Z Far distance. Defaults to 10000.0.
            aspect (float, optional): Ratio between width and height. Defaults to 1.

        """
        self._top: Plane = None
        self._bottom: Plane = None
        self._right: Plane = None
        self._left: Plane = None
        self._far: Plane = None
        self._near: Plane = None

        # values to calculate the frustum planes
        self._fov_y: float = fov_y
        self._z_far: float = z_far
        self._z_near: float = z_near
        self._aspect: float = aspect
        self._up: glm.vec3 = up
        self._right_vector: glm.vec3 = right
        self._front: glm.vec3 = front
        self._position: glm.vec3 = position

        self.calculate_frustum()

    def __str__(self) -> str:
        """Show the info of the planes of the frustum if they are set."""
        string = ''

        if self._near is not None:
            string += (
                'Near:  \n Normal: '
                + str(self.near.normal)
                + '\n Distance: '
                + str(self.near.distance)
                + '\n Center: '
                + str(self.near.point)
                + '\n'
            )
        if self._far is not None:
            string += (
                'Far:   \n Normal: '
                + str(self.far.normal)
                + '\n Distance: '
                + str(self.far.distance)
                + '\n Center: '
                + str(self.far.point)
                + '\n'
            )
        if self._right is not None:
            string += (
                'Right: \n Normal: '
                + str(self.right.normal)
                + '\n Distance: '
                + str(self.right.distance)
                + '\n Center: '
                + str(self.right.point)
                + '\n'
            )
        if self._left is not None:
            string += (
                'Left:  \n Normal: '
                + str(self.left.normal)
                + '\n Distance: '
                + str(self.left.distance)
                + '\n Center: '
                + str(self.left.point)
                + '\n'
            )
        if self._top is not None:
            string += (
                'Top:   \n Normal: '
                + str(self.top.normal)
                + '\n Distance: '
                + str(self.top.distance)
                + '\n Center: '
                + str(self.top.point)
                + '\n'
            )
        if self._bottom is not None:
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

    # ---------------------------- Getters and Setters --------------------------- #
    @property
    def fov_y(self) -> float:
        """Field of view for the y axis."""
        return self._fov_y

    @fov_y.setter
    def fov_y(self, value: float) -> None:
        if not isinstance(value, float):
            print('Frustum.fov_y Invalid Value')
            return
        self._fov_y = value

    @property
    def z_far(self) -> float:
        """Distance from the origin to end the frustum."""
        return self._z_far

    @z_far.setter
    def z_far(self, value: float) -> None:
        if not isinstance(value, float):
            print('Frustum.z_far Invalid Value')
            return
        self._z_far = value

    @property
    def z_near(self) -> float:
        """Distance from the origin to start the frustum."""
        return self._z_near

    @z_near.setter
    def z_near(self, value: float) -> None:
        if not isinstance(value, float):
            print('Frustum.z_near Invalid Value')
            return
        self._z_near = value

    @property
    def aspect(self) -> float:
        """Ratio between the width and height of the frustum front plane."""
        return self._aspect

    @aspect.setter
    def aspect(self, value: float) -> None:
        if not isinstance(value, float):
            print('Frustum.aspect Invalid Value')
            return
        self._aspect = value

    @property
    def up(self) -> glm.vec3:
        """Up vector for calculating the frustum."""
        return self._up

    @up.setter
    def up(self, value: glm.vec3) -> None:
        if not isinstance(value, glm.vec3):
            print('Frustum.up Invalid Value')
            return
        self._up = value

    @property
    def right_vector(self) -> glm.vec3:
        """Right vector for calculating the frustum."""
        return self._right_vector

    @right_vector.setter
    def right_vector(self, value: glm.vec3) -> None:
        if not isinstance(value, glm.vec3):
            print('Frustum.right Invalid Value')
            return
        self._right_vector = value

    @property
    def front(self) -> glm.vec3:
        """Front vector for calculating the frustum."""
        return self._front

    @front.setter
    def front(self, value: glm.vec3) -> None:
        if not isinstance(value, glm.vec3):
            print('Frustum.front Invalid Value')
            return
        self._front = value
        
    @property
    def position(self) -> float:
        """Position vector for calculating the frustum."""
        return self._position

    @position.setter
    def position(self, value: float) -> None:
        if not isinstance(value, glm.vec3):
            print('Frustum.position Invalid Value')
            return
        self._position = value

    # ------------------------------ Public methods ------------------------------ #
    def calculate_frustum(self) -> None:
        """Calculate the frustum planes."""
        # if any required value is not properly set, return an error.
        if (
            (not self._fov_y)
            or (not self._aspect)
            or (not self._z_far)
            or (not self._z_near)
            or (not self._up)
            or (not self._right_vector)
            or (not self._front)
            or (not self._position)
        ):
            print('Frustum.calculate_frustum() Missing properties')
            return

        half_v_side: float = self._z_far * math.tan(self._fov_y * 0.5)

        half_h_side: float = half_v_side * self._aspect

        front_mult_far: glm.vec3 = self._z_far * self._front

        self._near = Plane(self._position + self._z_near * self._front, self._front)

        self._far = Plane(self._position + front_mult_far, -self._front)

        self._right = Plane(self._position, glm.cross(front_mult_far + self._right_vector * half_h_side, self._up))

        self._left = Plane(self._position, glm.cross(self._up, front_mult_far - self._right_vector * half_h_side))

        self._top = Plane(self._position, glm.cross(self._right_vector, front_mult_far + self._up * half_v_side))

        self._bottom = Plane(self._position, glm.cross(front_mult_far - self._up * half_v_side, self._right_vector))

    def check_visibility(self, center: glm.vec3, radius: float) -> bool:
        """Check if a bounding sphere is inside the the Frustum.

        Args:
            center (glm.vec3): Vector of the position of the sphere to check.
            radius (float): Radius of the sphere to check.

        Returns:
            bool: True or False depending on if the sphere is inside the Frustum.

        """
        if not self._is_on_forward_plane(self._near, center, radius):
            return False
        if not self._is_on_forward_plane(self._bottom, center, radius):
            return False
        if not self._is_on_forward_plane(self._far, center, radius):
            return False
        if not self._is_on_forward_plane(self._left, center, radius):
            return False
        if not self._is_on_forward_plane(self._right, center, radius):
            return False
        if not self._is_on_forward_plane(self._top, center, radius):  # noqa: SIM103
            return False

        return True

    # ------------------------------ Private methods ----------------------------- #
    def _is_on_forward_plane(self, plane: Plane, center: glm.vec3, radius: float) -> any:
        return glm.dot(plane.normal, center) - plane.distance > -radius
