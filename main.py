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
from renderer.Renderer import Renderer
from controller.Controller import Controller
from ui.UI import UI


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
    # UI object
    ui = UI()

    # printer object to print render information
    printer = Printer(interval = 2000)

    # execution timer
    frametime = Timer()

    # time passed between frames
    dt = 0

    # 60 tps
    tickrate = 1000.0 / 60.0

    # 60 fps
    # framerate = 1000.0 / 1000.0
    
    tick_accumulator = 0.0
    # frame_accumulator = 0.0

    # game loop
    while not glfw.window_should_close(window.window):
        # calculate the elapsed time from the last cycle
        dt = frametime.elapsed()
        frametime.reset()

        tick_accumulator += dt
        # frame_accumulator += dt

        while tick_accumulator > tickrate:
            glfw.poll_events()
            # ui.implementation.process_inputs()
            # update the game depending on the inputs
            controller.update(window, tickrate)

            scene.update(tickrate)

            tick_accumulator -= tickrate
            
        # if frame_accumulator > framerate:
        # render the scene to the screen
        renderer.render()
        ui.draw()
        glfw.swap_buffers(window.window)
        # frame_accumulator -= framerate

        # print the rendering information
        printer.write(verbose=False, frametime=dt)

    glfw.terminate()
            

if __name__ == "__main__":
    main()