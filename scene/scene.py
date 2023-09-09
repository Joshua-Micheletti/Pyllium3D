from renderer.RendererManager import RendererManager

def setup():
    rm = RendererManager()

    rm.new_mesh("gally", "models/gally.obj")

    rm.scale("gally", 100, 100, 100)

    for i in range(640):
        rm.new_mesh("box" + str(i), "models/gally.obj")