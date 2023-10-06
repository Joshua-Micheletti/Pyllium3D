import imgui

from window.Window import Window
from renderer.RendererManager import RendererManager
from utils.colors import gui_colors

class RightWindow:
    def __init__(self):
        self.width = 0
        self.height = 0

        self.selected_model_index = 0
        self.selected_model = ""

    def draw(self, states, dimensions):
        if states["right_window"] == False:
            dimensions["right_window_width"] = 0
            return(states, dimensions)
        
        window = Window()
        rm = RendererManager()

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


        states["right_window/model_header"], _ = imgui.collapsing_header("Model")

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
                imgui.indent()

                position = rm.positions[self.selected_model]
                rotation = rm.rotations[self.selected_model]
                scale = rm.scales[self.selected_model]

                item_spacing = 2.0
                normal_item_spacing = 8.0

                available_slider_width = dimensions["right_window_width"] - \
                                         dimensions["indent_size"] * 3 - \
                                         item_spacing * 3 - \
                                         normal_item_spacing * 3 - \
                                         imgui.calc_text_size("Z").x

                imgui.push_item_width(available_slider_width / 3)
                
                # with imgui.font(self.font):
                # position
                imgui.text("Position:")

                imgui.align_text_to_frame_padding()
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
                imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.red)
                imgui.text("X")
                imgui.pop_style_color()
                imgui.same_line()
                changed, x = imgui.drag_float("###p.x", position.x, change_speed = 0.1)
                imgui.pop_style_var()
                imgui.same_line()
                
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
                imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.green)
                imgui.text("Y")
                imgui.pop_style_color()
                imgui.same_line()
                changed, y = imgui.drag_float("###p.y", position.y, change_speed = 0.1)
                imgui.pop_style_var(1)
                imgui.same_line()

                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
                imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.blue)
                imgui.text("Z")
                imgui.pop_style_color()
                imgui.same_line()
                changed, z = imgui.drag_float("###p.z", position.z, change_speed = 0.1)
                imgui.pop_style_var()

                rm.place(self.selected_model, x, y, z)

                # rotation
                imgui.text("Rotation:")

                imgui.align_text_to_frame_padding()
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
                imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.red)
                imgui.text("X")
                imgui.pop_style_color()
                imgui.same_line()
                changed, x = imgui.drag_float("###r.x", rotation.x)
                imgui.pop_style_var(1)

                imgui.same_line()
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
                imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.green)
                imgui.text("Y")
                imgui.pop_style_color()
                imgui.same_line()
                changed, y = imgui.drag_float("###r.y", rotation.y)
                imgui.pop_style_var()
                
                imgui.same_line()
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
                imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.blue)
                imgui.text("Z")
                imgui.pop_style_color()
                imgui.same_line()
                changed, z = imgui.drag_float("###r.z", rotation.z)
                imgui.pop_style_var()
                rm.rotate(self.selected_model, x, y, z)

                # scale
                imgui.text("Scale:")
                
                imgui.align_text_to_frame_padding()
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
                imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.red)
                imgui.text("X")
                imgui.pop_style_color()
                imgui.same_line()
                changed, x = imgui.drag_float("###s.x", scale.x, change_speed = 0.1)
                imgui.pop_style_var()

                imgui.same_line()
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
                imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.green)
                imgui.text("Y")
                imgui.pop_style_color()
                imgui.same_line()
                changed, y = imgui.drag_float("###s.y", scale.y, change_speed = 0.1)
                imgui.pop_style_var()

                imgui.same_line()
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
                imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.blue)
                imgui.text("Z")
                imgui.pop_style_color()
                imgui.same_line()
                changed, z = imgui.drag_float("###s.z", scale.z, change_speed = 0.1)
                imgui.pop_style_var()

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

        imgui.pop_style_var()
        imgui.end()

        return(states, dimensions)