# module to get the parameters from the command line
import sys
# module to create the window
import glfw

import scene

# local modules
from utils import argument_parser as ap
from utils.Timer import Timer
from utils.Printer import Printer

from window.Window import Window
from renderer.RendererManager import RendererManager
from renderer.Renderer import Renderer
from controller.Controller import Controller


def main():
    # parse the arguments from the command line
    # ap.parse_arguments(sys.argv)

    # window object
    window = Window()
    # setup the scene
    scene.setup()
    # renderer object
    renderer = Renderer()
    # controller object
    controller = Controller()

    # printer object to print render information
    printer = Printer(interval = 2000)

    # execution timer
    frametime = Timer()

    # time passed between frames
    dt = 0
    
    # game loop
    while not glfw.window_should_close(window.window):
        # update the game depending on the inputs
        controller.update(window, dt)

        # render the scene to the screen
        renderer.render()
        
        # refresh the screen and handle events
        glfw.swap_buffers(window.window)
        glfw.poll_events()

        # calculate the time it took to render this cycle
        dt = frametime.elapsed()
        frametime.reset()

        # print the rendering information
        printer.write(frametime=dt, verbose=False)
        
    glfw.terminate()
            

if __name__ == "__main__":
    main()