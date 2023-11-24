import imgui

from window.window import Window
from renderer.renderer_manager import RendererManager

from ui.components.transformation import Transformation
from ui.components.components import Components

class RightWindow:
    def __init__(self):
        self.width = 0
        self.height = 0

        self.selected_model_index = 0
        self.selected_model = ""

        self.selected_light_index = 0
        self.selected_light = ""

        self.transformation = Transformation()
        self.components = Components()

    def draw(self, states, dimensions):
        if states["right_window"] == False:
            dimensions["right_window_width"] = 0
            return(states, dimensions)
        
        window = Window()
        rm = RendererManager()
        style = imgui.get_style()

        imgui.set_next_window_position(window.width, dimensions["main_menu_height"], pivot_x = 1.0)
        imgui.set_next_window_size_constraints((100, window.height - dimensions["main_menu_height"]), (window.width / 2, window.height - dimensions["main_menu_height"]))

        if states["first_draw"]:
            imgui.set_next_window_size(window.width / 6, window.height - dimensions["main_menu_height"])

        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0.0, 0.0))
        _, states["right_window"] = imgui.begin("right_window", flags = imgui.WINDOW_NO_TITLE_BAR)

        wsize = imgui.get_window_size()
        dimensions["right_window_width"] = wsize.x
        self.width = wsize.x
        self.height = wsize.y


        states["right_window/model_header"], _ = imgui.collapsing_header("Models")

        if states["right_window/model_header"]:
            imgui.indent()

            models = list(rm.models.keys())
            imgui.push_item_width(dimensions["right_window_width"] - dimensions["indent_size"] * 2)
            clicked, self.selected_model_index = imgui.combo("", self.selected_model_index, models)
            imgui.pop_item_width()
            
            if clicked:
                self.selected_model = models[self.selected_model_index]

            imgui.unindent()

        if len(self.selected_model) != 0:
            states = self.transformation.draw(states, self.selected_model)
            states = self.components.draw(states, dimensions, self.selected_model)
            

        states["right_window/lights_header"], _ = imgui.collapsing_header("Lights")

        if states["right_window/lights_header"]:
            imgui.indent()

            lights = list(rm.lights.keys())
            imgui.push_item_width(dimensions["right_window_width"] - dimensions["indent_size"] * 2)
            clicked, self.selected_light_index = imgui.combo("###lights", self.selected_light_index, lights)
            imgui.pop_item_width()

            if clicked:
                self.selected_light = lights[self.selected_light_index]

            imgui.unindent()

        if len(self.selected_light) != 0:
            available_region = imgui.get_content_region_available()

            item_width = available_region.x - style.indent_spacing * 2

            imgui.push_item_width(item_width)

            imgui.indent()
            light_color_r = rm.light_colors[rm.lights[self.selected_light] * 3 + 0]
            light_color_g = rm.light_colors[rm.lights[self.selected_light] * 3 + 1]
            light_color_b = rm.light_colors[rm.lights[self.selected_light] * 3 + 2]

            imgui.text("Light Color:")
            changed, light_color = imgui.color_edit3("###light_color", light_color_r, light_color_g, light_color_b)
            if changed:
                rm.set_light_color(self.selected_light, *light_color)

            imgui.text("Strength:")
            changed, light_strength = imgui.drag_float("###strength", rm.light_strengths[rm.lights[self.selected_light]])
            if changed:
                rm.set_light_strength(self.selected_light, light_strength)

            imgui.pop_item_width()

            imgui.unindent()
        


        imgui.pop_style_var()
        imgui.end()

        return(states, dimensions)