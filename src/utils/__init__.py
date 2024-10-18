"""Utils module."""

from utils.argument_parser import parse_arguments
from utils.colors import Colors, GuiColors
from utils.framebuffer import (
    check_framebuffer_status,
    create_cubemap_framebuffer,
    create_framebuffer,
    create_g_buffer,
    create_multisample_framebuffer,
)
from utils.matrix import create_projection_matrix, create_view_cubemap_matrices, create_view_matrix, get_ogl_matrix

# from utils.config import *
from utils.messages import (
    print_error,
    print_info,
    print_success,
    print_time,
    print_warning,
)
from utils.opengl import get_query_time
from utils.profiler import profile

# from utils.printer import * # causes a circular import
from utils.singleton import Singleton
from utils.timer import Timer, timeit
from utils.vbo_indexer import (
    get_similar_vertex_index,
    index_vertices,
    index_vertices_multi_thread,
    index_vertices_st_worker,
)

__all__ = [
    'parse_arguments',
    'Colors',
    'GuiColors',
    'print_error',
    'print_info',
    'print_success',
    'print_time',
    'print_warning',
    'profile',
    'Singleton',
    'Timer',
    'timeit',
    'get_similar_vertex_index',
    'index_vertices',
    'index_vertices_multi_thread',
    'index_vertices_st_worker',
    'check_framebuffer_status',
    'create_framebuffer',
    'create_multisample_framebuffer',
    'create_cubemap_framebuffer',
    'create_projection_matrix',
    'create_view_matrix',
    'get_ogl_matrix',
    'create_view_cubemap_matrices',
    'create_g_buffer',
    'get_query_time',
]
