"""Plane module."""

import glm


class Plane:
    """Plane class."""

    def __init__(self, point: glm.vec3, normal: glm.vec3) -> None:
        """Calculate the plane properties.

        Args:
            point (glm.vec3): Point in the plane
            normal (glm.vec3): Normal vector of the plane

        """
        self._normal: glm.vec3 = glm.normalize(normal)
        self._distance: float = glm.dot(self._normal, point)

    @property
    def normal(self) -> glm.vec3:
        """Normal vector of the plane."""
        return self._normal

    @property
    def distance(self) -> float:
        """Distance value from the origin."""
        return self._distance
