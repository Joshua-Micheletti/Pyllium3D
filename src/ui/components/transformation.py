import imgui

from renderer.renderer_manager import RendererManager
from utils import GuiColors


class Transformation:
    def __init__(self) -> None:
        pass

    def draw(self, states: dict[str, bool], selected_model: str) -> dict[str, bool]:
        rm = RendererManager()
        style = imgui.get_style()

        states['right_window/transformation_header'], _ = imgui.collapsing_header('Transformation')

        if states['right_window/transformation_header']:
            available_region = imgui.get_content_region_available()

            imgui.indent()

            position = rm.positions[selected_model]
            rotation = rm.rotations[selected_model]
            scale = rm.scales[selected_model]

            item_spacing = 2.0

            slider_width = (
                available_region.x
                - style.indent_spacing
                - imgui.calc_text_size('X').x
                - style.item_spacing.x
                - style.indent_spacing
            )

            imgui.push_item_width(slider_width)

            # position
            imgui.text('Position:')

            imgui.align_text_to_frame_padding()
            imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
            imgui.push_style_color(imgui.COLOR_TEXT, *GuiColors.red)
            imgui.text('X')
            imgui.pop_style_color()
            imgui.same_line()
            changed_x, x = imgui.drag_float('###p.x', position.x, change_speed=0.1)
            imgui.pop_style_var()
            # imgui.same_line()

            imgui.align_text_to_frame_padding()
            imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
            imgui.push_style_color(imgui.COLOR_TEXT, *GuiColors.green)
            imgui.text('Y')
            imgui.pop_style_color()
            imgui.same_line()
            changed_y, y = imgui.drag_float('###p.y', position.y, change_speed=0.1)
            imgui.pop_style_var(1)
            # imgui.same_line()

            imgui.align_text_to_frame_padding()
            imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
            imgui.push_style_color(imgui.COLOR_TEXT, *GuiColors.blue)
            imgui.text('Z')
            imgui.pop_style_color()
            imgui.same_line()
            changed_z, z = imgui.drag_float('###p.z', position.z, change_speed=0.1)
            imgui.pop_style_var()

            if changed_x or changed_y or changed_z:
                rm.place(selected_model, x, y, z)

            # rotation
            imgui.text('Rotation:')

            imgui.align_text_to_frame_padding()
            imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
            imgui.push_style_color(imgui.COLOR_TEXT, *GuiColors.red)
            imgui.text('X')
            imgui.pop_style_color()
            imgui.same_line()
            changed_x, x = imgui.drag_float('###r.x', rotation.x)
            imgui.pop_style_var(1)

            # imgui.same_line()
            imgui.align_text_to_frame_padding()
            imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
            imgui.push_style_color(imgui.COLOR_TEXT, *GuiColors.green)
            imgui.text('Y')
            imgui.pop_style_color()
            imgui.same_line()
            changed_y, y = imgui.drag_float('###r.y', rotation.y)
            imgui.pop_style_var()

            # imgui.same_line()
            imgui.align_text_to_frame_padding()
            imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
            imgui.push_style_color(imgui.COLOR_TEXT, *GuiColors.blue)
            imgui.text('Z')
            imgui.pop_style_color()
            imgui.same_line()
            changed_z, z = imgui.drag_float('###r.z', rotation.z)
            imgui.pop_style_var()

            if changed_x or changed_y or changed_z:
                rm.rotate(selected_model, x, y, z)

            # scale
            imgui.text('Scale:')

            imgui.align_text_to_frame_padding()
            imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
            imgui.push_style_color(imgui.COLOR_TEXT, *GuiColors.red)
            imgui.text('X')
            imgui.pop_style_color()
            imgui.same_line()
            changed_x, x = imgui.drag_float('###s.x', scale.x, change_speed=0.1)
            imgui.pop_style_var()

            # imgui.same_line()
            imgui.align_text_to_frame_padding()
            imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
            imgui.push_style_color(imgui.COLOR_TEXT, *GuiColors.green)
            imgui.text('Y')
            imgui.pop_style_color()
            imgui.same_line()
            changed_y, y = imgui.drag_float('###s.y', scale.y, change_speed=0.1)
            imgui.pop_style_var()

            # imgui.same_line()
            imgui.align_text_to_frame_padding()
            imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (item_spacing, 8.0))
            imgui.push_style_color(imgui.COLOR_TEXT, *GuiColors.blue)
            imgui.text('Z')
            imgui.pop_style_color()
            imgui.same_line()
            changed_z, z = imgui.drag_float('###s.z', scale.z, change_speed=0.1)
            imgui.pop_style_var()

            if changed_x or changed_y or changed_z:
                rm.scale(selected_model, x, y, z)

            imgui.pop_item_width()
            imgui.unindent()

        return states
