import imgui

from window.Window import Window

class LeftWindow:
    def __init__(self):
        self.width = 0
        self.height = 0

    def draw(self, states, dimensions):
        if states["left_window"] == False:
            dimensions["left_window_width"] = 0
            return(states, dimensions)
        
        window = Window()

        imgui.set_next_window_position(0, dimensions["main_menu_height"])
        imgui.set_next_window_size_constraints((100, window.height - dimensions["main_menu_height"]),
                                               (window.width / 2, window.height - dimensions["main_menu_height"]))

        if states["first_draw"]:
            imgui.set_next_window_size(window.width / 6, window.height - dimensions["main_menu_height"])
        
        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0.0, 0.0))
        _, states["left_window"] = imgui.begin("left_window", flags = imgui.WINDOW_NO_TITLE_BAR)

        wsize = imgui.get_window_size()
        dimensions["left_window_width"] = wsize.x
        self.width = wsize.x
        self.height = wsize.y

        imgui.text("Hellow!")

        imgui.pop_style_var()

        imgui.end()

        return(states, dimensions)

