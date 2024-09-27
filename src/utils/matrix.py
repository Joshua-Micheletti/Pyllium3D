"""Utilities for creating and handling matrices."""

import glm
import numpy as np


def create_projection_matrix(
    width: int = 800, height: int = 600, fov: int = 60, near: float = 0.1, far: float = 10000.0
) -> glm.mat4:
    """Create a projection matrix with the specified caracteristics.

    Args:
        width (int, optional): Width of the projection. Defaults to 800.
        height (int, optional): Height of the projection. Defaults to 600.
        fov (int, optional): Field of View of the projection. Defaults to 60.
        near (float, optional): Near plane of the projection. Defaults to 0.1.
        far (float, optional): Far plane of the projection. Defaults to 10000.

    """
    return glm.perspective(glm.radians(fov), float(width) / float(height), near, far)


def create_view_matrix(position: glm.vec3 = None, front: glm.vec3 = None, world_up: glm.vec3 = None) -> glm.mat4:
    """Create a view matrix based on the incoming pointers.

    Args:
        position (glm.vec3, optional): Position of the camera. Defaults to (0, 0, 0).
        front (glm.vec3, optional): Direction the camera is looking at. Defaults to (1, 0, 0).
        world_up (glm.vec3, optional): Vector defining the up vector of the world. Defaults to (0, 1, 0).

    Returns:
        glm.mat4: View matrix

    """
    if not position:
        position = glm.vec3(0, 0, 0)

    if not front:
        front = glm.vec3(1, 0, 0)

    if not world_up:
        world_up = glm.vec3(0, 1, 0)

    return glm.lookAt(position, position + front, world_up)


def get_ogl_matrix(matrix: glm.mat4) -> any:
    """Get the OpenGL pointer to pass the matrix to the shader.

    Args:
        matrix (glm.mat4): Matrix to transform

    Returns:
        any: OpenGL compatible pointer containing the matrix data

    """
    return np.array(matrix.to_list(), dtype=np.float32)
