import imgui

from window.window import Window
from renderer.renderer_manager import RendererManager
from utils.colors import gui_colors

class RightWindow:
    def __init__(self):
        self.width = 0
        self.height = 0

        self.selected_model_index = 0
        self.selected_model = ""

        self.selected_light_index = 0
        self.selected_light = ""

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
            states["right_window/transformation_header"], _ = imgui.collapsing_header("Transformation")

            if states["right_window/transformation_header"]:
                available_region = imgui.get_content_region_available()

                imgui.indent()

                position = rm.positions[self.selected_model]
                rotation = rm.rotations[self.selected_model]
                scale = rm.scales[self.selected_model]

                item_spacing = 2.0
                normal_item_spacing = 8.0

                # available_slider_width = dimensions["right_window_width"] - \
                #                          dimensions["indent_size"] * 3 - \
                #                          item_spacing * 3 - \
                #                          normal_item_spacing * 3 - \
                #                          imgui.calc_text_size("Z").x
                slider_width = available_region.x \
                             - style.indent_spacing - imgui.calc_text_size("X").x - style.item_spacing.x - style.indent_spacing

                imgui.push_item_width(slider_width)
                
                # with imgui.font(self.font):
                # position
                imgui.text("Position:")

                imgui.align_text_to_frame_padding()
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
                imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.red)
                imgui.text("X")
                imgui.pop_style_color()
                imgui.same_line()
                changed_x, x = imgui.drag_float("###p.x", position.x, change_speed = 0.1)
                imgui.pop_style_var()
                # imgui.same_line()
                
                imgui.align_text_to_frame_padding()
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
                imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.green)
                imgui.text("Y")
                imgui.pop_style_color()
                imgui.same_line()
                changed_y, y = imgui.drag_float("###p.y", position.y, change_speed = 0.1)
                imgui.pop_style_var(1)
                # imgui.same_line()

                imgui.align_text_to_frame_padding()
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
                imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.blue)
                imgui.text("Z")
                imgui.pop_style_color()
                imgui.same_line()
                changed_z, z = imgui.drag_float("###p.z", position.z, change_speed = 0.1)
                imgui.pop_style_var()

                if changed_x or changed_y or changed_z:
                    rm.place(self.selected_model, x, y, z)

                # rotation
                imgui.text("Rotation:")

                imgui.align_text_to_frame_padding()
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
                imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.red)
                imgui.text("X")
                imgui.pop_style_color()
                imgui.same_line()
                changed_x, x = imgui.drag_float("###r.x", rotation.x)
                imgui.pop_style_var(1)

                # imgui.same_line()
                imgui.align_text_to_frame_padding()
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
                imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.green)
                imgui.text("Y")
                imgui.pop_style_color()
                imgui.same_line()
                changed_y, y = imgui.drag_float("###r.y", rotation.y)
                imgui.pop_style_var()
                
                # imgui.same_line()
                imgui.align_text_to_frame_padding()
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
                imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.blue)
                imgui.text("Z")
                imgui.pop_style_color()
                imgui.same_line()
                changed_z, z = imgui.drag_float("###r.z", rotation.z)
                imgui.pop_style_var()

                if changed_x or changed_y or changed_z:
                    rm.rotate(self.selected_model, x, y, z)

                # scale
                imgui.text("Scale:")
                
                imgui.align_text_to_frame_padding()
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
                imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.red)
                imgui.text("X")
                imgui.pop_style_color()
                imgui.same_line()
                changed_x, x = imgui.drag_float("###s.x", scale.x, change_speed = 0.1)
                imgui.pop_style_var()

                # imgui.same_line()
                imgui.align_text_to_frame_padding()
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
                imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.green)
                imgui.text("Y")
                imgui.pop_style_color()
                imgui.same_line()
                changed_y, y = imgui.drag_float("###s.y", scale.y, change_speed = 0.1)
                imgui.pop_style_var()

                # imgui.same_line()
                imgui.align_text_to_frame_padding()
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
                imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.blue)
                imgui.text("Z")
                imgui.pop_style_color()
                imgui.same_line()
                changed_z, z = imgui.drag_float("###s.z", scale.z, change_speed = 0.1)
                imgui.pop_style_var()

                if changed_x or changed_y or changed_z:
                    rm.scale(self.selected_model, x, y, z)

                imgui.pop_item_width()
                imgui.unindent()

        if len(self.selected_model) != 0:
            states["right_window/components_header"], _ = imgui.collapsing_header("Components")

            if states["right_window/components_header"]:
                imgui.indent()

                meshes = list(rm.vaos.keys())
                shaders = list(rm.shaders.keys())
                materials = list(rm.materials.keys())

                available_width = dimensions["right_window_width"] - dimensions["indent_size"] * 2

                imgui.push_item_width(available_width)

                imgui.text("Mesh")
                clicked, selected_mesh = imgui.combo("###combo_mesh", meshes.index(rm.models[self.selected_model].mesh), meshes)

                if clicked:
                    rm.models[self.selected_model].mesh = meshes[selected_mesh]

                imgui.text("Shader")
                clicked, selected_shader = imgui.combo("###combo_shader", shaders.index(rm.models[self.selected_model].shader), shaders)

                if clicked:
                    rm.models[self.selected_model].shader = shaders[selected_shader]


                imgui.text("Material")
                clicked, selected_material = imgui.combo("###combo_material", materials.index(rm.models[self.selected_model].material), materials)

                if clicked:
                    rm.models[self.selected_model].material = materials[selected_material]

                imgui.pop_item_width()

                imgui.unindent()

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