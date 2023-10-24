import imgui

class Crosshair:
    def __init__(self):
        self.color = (1.0, 1.0, 1.0, 0.5)
        self.radius = 3

    def draw(self):
        wsize = imgui.get_window_size()
        wpos = imgui.get_window_position()

        draw_list = imgui.get_window_draw_list()
        draw_list.add_circle_filled(wsize.x / 2 + wpos.x, wsize.y / 2 + wpos.y, self.radius, imgui.get_color_u32_rgba(*self.color))