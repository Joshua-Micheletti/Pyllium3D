# module to get the parameters from the command line
import sys
# module to create the window
import glfw
from OpenGL.GL import *

import scene

# local modules
from utils import argument_parser as ap
from utils.Timer import Timer
from utils.Printer import Printer

from window.Window import Window
from renderer.RendererManager import RendererManager
from renderer.Renderer import Renderer
from controller.Controller import Controller
from ui.UI import UI


def main():
    # window object
    window = Window()
    # setup the scene
    scene.setup()

    rm = RendererManager()
    # renderer object
    renderer = Renderer()
    # controller object
    controller = Controller()
    # UI object
    ui = UI()

    # printer object to print render information
    # printer = Printer(interval = 2000)

    # execution timer
    frametime = Timer()

    # time passed between frames
    dt = 0

    # 60 tps
    tickrate = 1000.0 / 60.0
    
    swaptime = Timer()
    swaptime.record()
    controltime = Timer()
    controltime.record()

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

        while tick_accumulator > tickrate:
            controltime.reset()
            glfw.poll_events()
            controller.update(window, tickrate)
            controltime.record()
            scene.update(tickrate)
            tick_accumulator -= tickrate
        
        rm.update()
        renderer.render()
        ui.draw(dt, swaptime.laps[-1], controltime.laps[-1])
        # print(f"swaptime: {swaptime.laps[-1]}")
        swaptime.reset()
        glfw.swap_buffers(window.window)
        
        swaptime.record()

        # print the rendering information
        # printer.write(verbose=False, frametime=dt)

    glfw.terminate()
            

if __name__ == "__main__":
    main()