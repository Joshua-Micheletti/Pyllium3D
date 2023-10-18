# module to create the window
import glfw
from OpenGL.GL import *

import scene

# local modules
from utils.Timer import Timer

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
    updatetime = Timer()
    updatetime.record()
    rmupdatetime = Timer()
    rmupdatetime.record()

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

            updatetime.reset()
            scene.update(tickrate)
            updatetime.record()

            tick_accumulator -= tickrate
        
        rmupdatetime.reset()
        rm.update()
        rmupdatetime.record()

        renderer.render()

        ui.draw(dt, swaptime.laps[-1], controltime.laps[-1], updatetime.laps[-1], rmupdatetime.laps[-1])

        swaptime.reset()
        glfw.swap_buffers(window.window)
        swaptime.record()

    glfw.terminate()
            

if __name__ == "__main__":
    main()