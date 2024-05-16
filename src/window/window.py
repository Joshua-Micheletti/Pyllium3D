import glfw
from OpenGL.GL import *
import glm
from glm import mat4x4
from icecream import ic

from utils import Singleton
from utils import messages
from utils import Config
from utils import timeit
from controller.controller import Controller

class Window(metaclass=Singleton):
    """Class that creates and handles all things regarding the window object
    """
    
    @timeit()
    def __init__(
        self,
        width: int = None,
        height: int = None,
        fullscreen: bool = None,
        name: str = None,
        fov: float = None,
        opengl_M: int = None,
        opengl_m: int = None,
        min_z: float = None,
        max_z: float = None
    ) -> None:
        """Constructor for the window object

        Args:
            width (int, optional): initial width of the window. Defaults to 800.
            height (int, optional): initial height of the window. Defaults to 600.
            fullscreen (bool, optional): initial fullscreen state. Defaults to False.
            name (str, optional): application name shown in the window. Defaults to 'Pyllium3D'.
            fov (float, optional): FOV of the view. Defaults to 60.
            opengl_M (int, optional): major OpenGL version to use. Defaults to 4.
            opengl_m (int, optional): minor OpenGL version to use. Defaults to 3.
            min_z (float, optional): min distance to render from. Defaults to 0.1.
            max_z (float, optional): max distance to render to. Defaults to 10000.
        """
        
        # default window configuration
        default_config = {
            'width': 800,
            'height': 600,
            'fullscreen': False,
            'opengl_M': 4,
            'opengl_m': 3,
            'name': 'Pyllium3D',
            'fov': 60,
            'min_z': 0.1,
            'max_z': 10000
        }
        
        Config().initialize_parameters(
            self,
            'window',
            default_config,
            width=width,
            height=height,
            fullscreen=fullscreen,
            name=name,
            fov=fov,
            opengl_M=opengl_M,
            opengl_m=opengl_m,
            min_z=min_z,
            max_z=max_z    
        )
        
        # initialize GLFW
        if not glfw.init():
            messages.print_error("Could not start GLFW")
            raise(RuntimeError("Could not start GLFW"))
        
        # set the OpenGL version
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, self.opengl_M)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, self.opengl_m)
        
        monitor = glfw.get_primary_monitor()
        screen = glfw.get_video_mode(monitor)[0]
        
        # fill the width and height fields with the initial window size
        if self.fullscreen:
            self.width = screen[0]
            self.height = screen[1]

        # create the GLFW window with the parameters given by the constructor      
        self.window = glfw.create_window(
            self.width,
            self.height,
            self.name,
            monitor if self.fullscreen else None,
            None
        )

        # check if the window was created
        if not self.window:
            messages.print_error("Could not start GLFW Window")
            glfw.terminate()
            raise(RuntimeError)

        # create a projection matrix with an orthogonal projection
        # self.projection_matrix = Matrix44.orthogonal_projection(-width/2, width/2, -height/2, height/2, -1, 1)
        self.projection_matrix: mat4x4 = glm.perspective(glm.radians(self.fov), float(self.width)/float(self.height), self.min_z, self.max_z)
        

        # set the callback functions related to the window
        # gets called everytime a key is pressed
        glfw.set_key_callback(self.window, key_callback)
        # gets called everytime the window is resized
        glfw.set_framebuffer_size_callback(self.window, framebuffer_size_callback)
        # gets called everytime a mouse event is triggered
        glfw.set_cursor_pos_callback(self.window, mouse_callback);

        # initialize the OpenGL context to the window
        glfw.make_context_current(self.window)
        # don't wait any screen refresh between frame swaps
        glfw.swap_interval(0)
        # disable the cursor above the window
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    def __repr__(self) -> str:
        return('Window obj')

    def get_ogl_matrix(self):
        return(glm.value_ptr(self.projection_matrix))



# pass the key presses to the controller
def key_callback(window, key, scancode, action, mods):
    if action == glfw.PRESS:
        Controller().handle_key_press(key, mods)
    if action == glfw.RELEASE:
        Controller().handle_key_release(key, mods)

# handle the resizing of the window
def framebuffer_size_callback(window, width, height):
    # glViewport(0, 0, width, height)
    Window().width = width
    Window().height = height
    Window().projection_matrix = glm.perspective(glm.radians(Window().fov), float(width)/float(height), 0.1, 10000.0)
    # RendererManager().update_dimensions(width, height)

# pass the mouse events to the controller
def mouse_callback(window, xpos, ypos):
    Controller().handle_mouse_movement(window, xpos, ypos)