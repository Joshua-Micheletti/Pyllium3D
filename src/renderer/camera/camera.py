"""Camera Module."""

import math

import glm

from renderer.camera.frustum import Frustum
from utils import create_view_matrix, get_ogl_matrix


class Camera:
    """Class implementing a camera."""

    def __init__(self) -> None:
        """Set the necessary vertices and matrices."""
        # postion vector
        self._position: glm.vec3 = glm.vec3(0.0, 0.0, 3.0)
        # direction vector
        self._front: glm.vec3 = glm.vec3(0.0, 0.0, -1.0)
        # world reference vector
        self._world_up: glm.vec3 = glm.vec3(0.0, 1.0, 0.0)

        # right vector, calculated based on the others
        self._right: glm.vec3 = glm.normalize(glm.cross(self._world_up, self._front))
        # up vector, calulated based on others
        self._up: glm.vec3 = glm.cross(self._front, self._right)

        # initialize the turn angles
        self._yaw: float = -90.0
        self._pitch: float = 0.0

        # create a frustum object for the camera
        self._frustum: Frustum = Frustum(position=self._position, front=self._front, right=self._right, up=self._up)

        # calculate the view matrix
        self._view_matrix = create_view_matrix(self._position, self._position + self._front, self._world_up)
        self._center_view_matrix = create_view_matrix(glm.vec3(0.0), self._front, self._world_up)
        self._ogl_view_matrix = get_ogl_matrix(self._view_matrix)
        self._ogl_center_view_matrix = get_ogl_matrix(self._center_view_matrix)

    # ---------------------------- Setters and Getters --------------------------- #
    @property
    def position(self) -> glm.vec3:
        """Vector keeping track of the camera's position in world space."""
        return self._position

    @property
    def view_matrix(self) -> glm.mat4:
        """View matrix of the camera."""
        return self._view_matrix

    @property
    def center_view_matrix(self) -> glm.mat4:
        """View matrix without the position factored in."""
        return self._center_view_matrix
    
    @property
    def ogl_view_matrix(self) -> glm.mat4:
        """OpenGL View matrix of the camera."""
        return self._ogl_view_matrix

    @property
    def ogl_center_view_matrix(self) -> glm.mat4:
        """OpenGL View matrix without the position factored in."""
        return self._ogl_center_view_matrix

    @property
    def frustum(self) -> Frustum:
        """Camera Frustum."""
        return self._frustum

    # ------------------------------- Interactions ------------------------------- #
    def move(self, amount: float) -> None:
        """Move the camera forwards or backwards.

        Args:
            amount (float): Amount of units to move forward or backwards

        """
        self._position += amount * self._front
        self._calculate_vectors()

    def place(self, x: float, y: float, z: float) -> None:
        """Place the camera at the specified location.

        Args:
            x (float): X coordinate of the camera
            y (float): Y coordinate of the camera
            z (float): Z coordinate of the camera

        """
        self._position = glm.vec3(x, y, z)
        self._calculate_vectors()

    def strafe(self, amount: float) -> None:
        """Move the camera left or right.

        Args:
            amount (float): Amount to strafe the camera by

        """
        self._position += amount * self._right
        self._calculate_vectors()

    def lift(self, amount: float) -> None:
        """Move the camera up or down.

        Args:
            amount (float): Amount to lift the camera by

        """
        self._position += amount * self._world_up
        self._calculate_vectors()

    def turn(self, yaw: float, pitch: float) -> None:
        """Turn the camera by the amounts of yaw and pitch respectively.

        Args:
            yaw (float): Yaw to add to the camera
            pitch (float): Pitch to add to the camera

        """
        # add up the new orientation
        self._yaw += yaw
        self._pitch += pitch

        # clamp the pitch
        if self._pitch > 89.0:
            self._pitch = 89.0
        if self._pitch < -89.0:
            self._pitch = -89.0

        # calculate the direction vector
        direction = glm.vec3(
            math.cos(glm.radians(self._yaw)) * math.cos(glm.radians(self._pitch)),
            math.sin(glm.radians(self._pitch)),
            math.sin(glm.radians(self._yaw)) * math.cos(glm.radians(self._pitch)),
        )

        # update the front vector
        self._front = glm.normalize(direction)
        # recalculate the rest of the vectors and view matrix
        self._calculate_vectors()

    # ------------------------------ Private methods ----------------------------- #
    # method to recalculate the vertices and view matrix
    def _calculate_vectors(self) -> None:
        self._right = glm.normalize(glm.cross(self._world_up, self._front))
        self._up = glm.cross(self._front, self._right)
        self._view_matrix = glm.lookAt(self._position, self._position + self._front, self._world_up)
        self._center_view_matrix = glm.lookAt(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0) + self._front, self._world_up)
        self._ogl_view_matrix = get_ogl_matrix(self._view_matrix)
        self._ogl_center_view_matrix = get_ogl_matrix(self._center_view_matrix)
        # self.view_matrix = create_view_matrix(self.position, self.position + self.front, self.world_up)
        # self.center_view_matrix = create_view_matrix(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0) + self.front, self.world_up)
        self._frustum.front = self._front
        self._frustum.up = self._up
        self._frustum.right_vector = self._right
        self._frustum.position = self._position

        self._frustum.calculate_frustum()
