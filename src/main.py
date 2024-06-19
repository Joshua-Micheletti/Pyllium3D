# module to create the window
import glfw

# import the scene
from physics.physics_world import PhysicsWorld
import scene

# local modules:
# utils
from utils import Timer

# window
from window import Window

# renderer manager
from renderer.renderer_manager.renderer_manager import RendererManager

# renderer
from renderer.renderer import Renderer
from renderer.raytracer import RayTracer

# controller
from controller.controller import Controller

from utils import Config

# from physics.physics_world import PhysicsWorld

from engine.engine import Engine

# user interface
from ui import UI


# -------------------------- Main ---------------------------
def main() -> None:
    # window object
    window: Window = Window()

    # setup the scene
    scene.setup()

    # get a reference to the renderer manager
    rm: RendererManager = RendererManager()

    pw: PhysicsWorld = PhysicsWorld()

    config = Config()

    engine: Engine = Engine()
    # renderer object
    renderer: Renderer = Renderer()

    raytracer: RayTracer = RayTracer()
    # controller object
    controller: Controller = Controller()
    # UI object
    ui: UI = UI()

    # execution timer
    frametime: Timer = Timer()

    # time passed between frames
    dt: float = 0

    # 60 tps
    tickrate: float = 1000.0 / 30.0

    # setup the timers to keep track of the execution time
    swaptime: Timer = Timer()
    swaptime.record()
    controltime: Timer = Timer()
    controltime.record()
    updatetime: Timer = Timer()
    updatetime.record()
    rmupdatetime: Timer = Timer()
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
            pw.update()
            engine.update()
            updatetime.record()

            tick_accumulator -= tickrate

        rmupdatetime.reset()
        scene.update(tickrate)
        rm.update()
        rm.update_instances()
        rmupdatetime.record()

        # renderer.render()
        raytracer.render()

        # ui.draw(
        #     dt,
        #     swaptime.get_last_record(),
        #     controltime.get_last_record(),
        #     updatetime.get_last_record(),
        #     rmupdatetime.get_last_record(),
        # )

        swaptime.reset()
        glfw.swap_buffers(window.window)
        swaptime.record()

    glfw.terminate()


if __name__ == "__main__":
    main()
