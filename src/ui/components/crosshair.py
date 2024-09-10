import imgui

from utils.config import Config


class Crosshair:
    def __init__(
        self,
        color_r: float = None,
        color_g: float = None,
        color_b: float = None,
        alpha: float = None,
        radius: int = None,
        outline_r: float = None,
        outline_g: float = None,
        outline_b: float = None,
        outline_alpha: float = None,
        outline_radius: int = None,
        outline_thickness: int = None,
    ) -> None:
        """Constructor method of the crosshair component

        Args:
            color_r (float, optional): red component of the crosshair. Defaults to 0.5.
            color_g (float, optional): green component of the crosshair. Defaults to 0.5.
            color_b (float, optional): blue component of the crosshair. Defaults to 0.5.
            alpha (float, optional): opacity of the crosshair. Defaults to 0.4.
            radius (int, optional): radius of the crosshair. Defaults to 3.
            outline_r (float, optional): red component of the crosshair. Defaults to 0.5.
            outline_g (float, optional): green component of the crosshair. Defaults to 0.5.
            outline_b (float, optional): blue component of the crosshair. Defaults to 0.5.
            outline_alpha (float, optional): opacity of the crosshair. Defaults to 0.4.
            outline_radius (int, optional): radius of the crosshair. Defaults to 4.
            outline_thickness (int, optional): radius of the crosshair. Defaults to 2.

        """
        default_values = {
            color_r: 0.5,
            color_g: 0.5,
            color_b: 0.5,
            alpha: 0.4,
            radius: 3,
            outline_r: 0.5,
            outline_g: 0.5,
            outline_b: 0.5,
            outline_alpha: 0.4,
            outline_radius: 4,
            outline_thickness: 2,
        }

        Config().initialize_parameters(
            self,
            'ui.crosshair',
            default_values,
            color_r=color_r,
            color_b=color_b,
            color_g=color_g,
            alpha=alpha,
            radius=radius,
            outline_r=outline_r,
            outline_g=outline_g,
            outline_b=outline_b,
            outline_alpha=outline_alpha,
            outline_radius=outline_radius,
            outline_thickness=outline_thickness,
        )

    def draw(self):
        wsize = imgui.get_window_size()
        wpos = imgui.get_window_position()

        draw_list = imgui.get_window_draw_list()
        draw_list.add_circle_filled(
            wsize.x / 2 + wpos.x,
            wsize.y / 2 + wpos.y,
            self.radius,
            imgui.get_color_u32_rgba(self.color_r, self.color_g, self.color_b, self.alpha),
        )
        draw_list.add_circle(
            wsize.x / 2 + wpos.x,
            wsize.y / 2 + wpos.y,
            self.outline_radius,
            imgui.get_color_u32_rgba(self.outline_r, self.outline_g, self.outline_b, self.outline_alpha),
            10,
            self.outline_thickness,
        )
