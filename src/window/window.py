import glfw
from OpenGL.GL import *
import glm

from utils import Singleton
from utils import messages
from utils import Config
from controller.controller import Controller
# from renderer.renderer_manager import RendererManager

class Window(metaclass=Singleton):
    """Class that creates and handles all things regarding the window object
    """
    
    def __init__(self, width = 800, height = 600, name = "Pyphics", opengl_M = 4, opengl_m = 3) -> None:
        setup = Config().setup
        
        # initialize GLFW
        if not glfw.init():
            messages.print_error("Could not start GLFW")
            raise(RuntimeError)
        
        # set the OpenGL version
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, opengl_M)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, opengl_m)
        
        monitor = glfw.get_primary_monitor()
        screen = glfw.get_video_mode(monitor)[0]
        
        # fill the width and height fields with the initial window size
        if setup['window']['fullscreen']:
            self.width = screen[0]
            self.height = screen[1]
        else:
            self.width = width
            self.height = height

        # create the GLFW window with the parameters given by the constructor      
        self.window = glfw.create_window(
            self.width,
            self.height,
            name,
            monitor if setup['window']['fullscreen'] else None,
            None
        )

        # check if the window was created
        if not self.window:
            messages.print_error("Could not start GLFW Window")
            glfw.terminate()
            raise(RuntimeError)

        # variable to set the FOV of the window
        self.fov = setup['window']['fov']

        # create a projection matrix with an orthogonal projection
        # self.projection_matrix = Matrix44.orthogonal_projection(-width/2, width/2, -height/2, height/2, -1, 1)
        self.projection_matrix = glm.perspective(glm.radians(self.fov), float(width)/float(height), setup['window']['min_z'], setup['window']['max_z'])
        

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

    def get_ogl_matrix(self):
        return(glm.value_ptr(self.projection_matrix))
        # return(glm.value_ptr(glm.mat4(1)))


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