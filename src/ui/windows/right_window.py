import imgui

from physics.physics_world import PhysicsWorld
from renderer.renderer_manager.renderer_manager import RendererManager
from ui.components import Components, Transformation
from ui.windows.resizable_window import ResizableWindow
from utils.colors import gui_colors
from window import Window


class RightWindow(ResizableWindow):
    def __init__(self):
        super().__init__('left')

        self.selected_model_index: int = 0
        self.selected_model: str = ''

        self.selected_light_index: int = 0
        self.selected_light: str = ''

        self.selected_physics_body_index: int = 0
        self.selected_physics_body: str = ''

        self.transformation = Transformation()
        self.components = Components()

    def draw(self, states, dimensions):
        if states['right_window'] == False:
            dimensions['right_window_width'] = 0
            return (states, dimensions)

        window = Window()
        rm = RendererManager()
        pw = PhysicsWorld()
        style = imgui.get_style()

        imgui.set_next_window_position(window.width, dimensions['main_menu_height'], pivot_x=1.0)
        imgui.set_next_window_size(self.width, self.height)

        imgui.set_next_window_size_constraints(
            (100, window.height - dimensions['main_menu_height']),
            (window.width / 2, window.height - dimensions['main_menu_height']),
        )

        if states['first_draw']:
            imgui.set_next_window_size(window.width / 6, window.height - dimensions['main_menu_height'])

        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0.0, 0.0))
        _, states['right_window'] = imgui.begin(
            'right_window', flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE
        )

        wsize = imgui.get_window_size()
        dimensions['right_window_width'] = wsize.x
        self.width = wsize.x
        self.height = wsize.y

        states['right_window/model_header'], _ = imgui.collapsing_header('Models')

        if states['right_window/model_header']:
            imgui.indent()

            models = list(rm.models.keys())
            imgui.push_item_width(dimensions['right_window_width'] - dimensions['indent_size'] * 2)
            clicked, self.selected_model_index = imgui.combo('', self.selected_model_index, models)
            imgui.pop_item_width()

            if clicked:
                self.selected_model = models[self.selected_model_index]

            imgui.unindent()

        if len(self.selected_model) != 0:
            states = self.transformation.draw(states, self.selected_model)
            states = self.components.draw(states, dimensions, self.selected_model)

        states['right_window/lights_header'], _ = imgui.collapsing_header('Lights')

        if states['right_window/lights_header']:
            imgui.indent()

            lights = list(rm.lights.keys())
            imgui.push_item_width(dimensions['right_window_width'] - dimensions['indent_size'] * 2)
            clicked, self.selected_light_index = imgui.combo('###lights', self.selected_light_index, lights)
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

            imgui.text('Light Color:')
            changed, light_color = imgui.color_edit3('###light_color', light_color_r, light_color_g, light_color_b)
            if changed:
                rm.set_light_color(self.selected_light, *light_color)

            imgui.text('Strength:')
            changed, light_strength = imgui.drag_float(
                '###strength', rm.light_strengths[rm.lights[self.selected_light]]
            )
            if changed:
                rm.set_light_strength(self.selected_light, light_strength)

            imgui.pop_item_width()

            imgui.unindent()

        states['right_window/physics_body_header'], _ = imgui.collapsing_header('Physics Bodies')

        if states['right_window/physics_body_header']:
            imgui.indent()

            physics_bodies = list(pw.rigid_bodies.keys())
            imgui.push_item_width(dimensions['right_window_width'] - dimensions['indent_size'] * 2)
            clicked, self.selected_physics_body_index = imgui.combo(
                '###physics_bodies', self.selected_physics_body_index, physics_bodies
            )
            imgui.pop_item_width()

            if clicked:
                self.selected_physics_body = physics_bodies[self.selected_physics_body_index]

            imgui.unindent()

        if len(self.selected_physics_body) != 0:
            available_region = imgui.get_content_region_available()

            item_spacing = 2.0

            item_width = available_region.x - style.indent_spacing * 2

            imgui.push_item_width(item_width)

            imgui.indent()

            position, rotation = pw.get_position_rotation(self.selected_physics_body)

            # position
            imgui.text('Position:')

            imgui.align_text_to_frame_padding()
            imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
            imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.red)
            imgui.text('X')
            imgui.pop_style_color()
            imgui.same_line()
            changed_x, x = imgui.drag_float('###pb.x', position[0], change_speed=0.1)
            imgui.pop_style_var()
            # imgui.same_line()

            imgui.align_text_to_frame_padding()
            imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
            imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.green)
            imgui.text('Y')
            imgui.pop_style_color()
            imgui.same_line()
            changed_y, y = imgui.drag_float('###pb.y', position[1], change_speed=0.1)
            imgui.pop_style_var(1)
            # imgui.same_line()

            imgui.align_text_to_frame_padding()
            imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
            imgui.push_style_color(imgui.COLOR_TEXT, *gui_colors.blue)
            imgui.text('Z')
            imgui.pop_style_color()
            imgui.same_line()
            changed_z, z = imgui.drag_float('###pb.z', position[2], change_speed=0.1)
            imgui.pop_style_var()

            if changed_x or changed_y or changed_z:
                pw.place(self.selected_physics_body, x, y, z)

            imgui.pop_item_width()

            imgui.unindent()

        self.handle_resize()

        imgui.pop_style_var()
        imgui.end()

        return (states, dimensions)
