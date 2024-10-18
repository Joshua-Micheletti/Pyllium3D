"""OpenGL utilities."""

# ruff: noqa: F403, F405

from OpenGL.GL import *


def get_query_time(opengl_query: int) -> float:
    """Get the elapsed time from a query.

    Args:
        opengl_query (int): OpenGL query

    Returns:
        float: Elapsed time in ms

    """
    available = glGetQueryObjectiv(opengl_query, GL_QUERY_RESULT_AVAILABLE)
    # busy wait until the query is available
    while not available:
        available = glGetQueryObjectiv(opengl_query, GL_QUERY_RESULT_AVAILABLE)

    return glGetQueryObjectuiv(opengl_query, GL_QUERY_RESULT) / 1000000
