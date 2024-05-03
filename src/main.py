# module to create the window
import glfw

# import the scene
import scene

# local modules:
# utils
from utils import Timer

# window
from window import Window

# renderer manager
from renderer.renderer_manager import RendererManager

# renderer
from renderer.renderer import Renderer

# controller
from controller.controller import Controller

from utils import Config

# from physics.physics_world import PhysicsWorld

from engine.engine import Engine

# user interface
from ui import UI


# -------------------------- Main ---------------------------
def main():
    setup = Config().setup

    # window object
    window = Window(
        width=setup["window"]["width"],
        height=setup["window"]["height"],
        name=setup["application_name"],
        opengl_M=setup["api"]["opengl_major"],
        opengl_m=setup["api"]["opengl_minor"]
    )
    
    # setup the scene
    scene.setup()

    # get a reference to the renderer manager
    rm = RendererManager()

    # pw = PhysicsWorld()

    config = Config()

    engine = Engine()
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
    tickrate = 1000.0 / 30.0

    # setup the timers to keep track of the execution time
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
            # pw.update()
            # engine.update()
            updatetime.record()

            tick_accumulator -= tickrate

        rmupdatetime.reset()
        scene.update(tickrate)
        rm.update()
        rm.update_instances()
        rmupdatetime.record()

        # cProfile.run("Renderer().render()")
        renderer.render()

        ui.draw(
            dt,
            swaptime.get_last_record(),
            controltime.get_last_record(),
            updatetime.get_last_record(),
            rmupdatetime.get_last_record(),
        )

        swaptime.reset()
        glfw.swap_buffers(window.window)
        swaptime.record()

    glfw.terminate()


if __name__ == "__main__":
    main()
