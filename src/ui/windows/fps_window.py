import imgui
from array import array

from window.window import Window
from renderer.renderer import Renderer

from ui.components.graph import Graph

class FpsWindow:
    def __init__(self):
        self.width = 0
        self.height = 0

        self.fps_values = []
        self.frametime_values = []
        self.rendertime_values = []
        self.ui_time_values = []

        self.fps_graph = Graph("FPS:")
        self.frametime_graph =  Graph("Frametime: ", scale_max = 60)
        self.rendertime_graph = Graph("Rendertime:", scale_max = 60)
        self.ui_time_graph =    Graph("UI:        ", scale_max = 60)
        self.swaptime_graph =   Graph("Swaptime:  ", scale_max = 60)
        self.control_graph =    Graph("Control:   ", scale_max = 60)
        self.update_graph =     Graph("Update:    ", scale_max = 60)
        self.rm_update_graph =  Graph("RM Update: ", scale_max = 60)

    def draw(self, states, dimensions, dt, ui_time, swaptime, controltime, updatetime, rmupdatetime):
        if states["fps_window"] == False:
            return(states, dimensions)
        
        window = Window()

        imgui.set_next_window_position(window.width - dimensions["right_window_width"], dimensions["main_menu_height"], pivot_x = 1.0)
        imgui.set_next_window_size_constraints((200, 60), (window.width / 2, window.height / 2 - dimensions["main_menu_height"]))

        _, states["fps_window"] = imgui.begin("fps_window", flags = imgui.WINDOW_NO_TITLE_BAR)

        self.fps_graph.draw(1000 / dt)

        states["fps_window/details_header"], _ = imgui.collapsing_header("Details")

        if states["fps_window/details_header"]:
            self.frametime_graph.draw(dt)
            self.rendertime_graph.draw(Renderer().timer.get_last_record())
            self.ui_time_graph.draw(ui_time)
            self.swaptime_graph.draw(swaptime)
            self.control_graph.draw(controltime)
            self.update_graph.draw(updatetime)
            self.rm_update_graph.draw(rmupdatetime)

        imgui.end()

        return(states, dimensions)