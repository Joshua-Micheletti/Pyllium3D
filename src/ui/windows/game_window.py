import imgui
from OpenGL.GL import glViewport

from renderer.raster_renderer.raster_renderer import RasterRenderer
from renderer.renderer_manager.renderer_manager import RendererManager
from ui.components import Crosshair
from window import Window


class GameWindow:
    def __init__(self) -> None:
        self.width = 0
        self.height = 0
        self.crosshair = Crosshair()

    def draw(self, states: dict[str, bool], dimensions: dict[str, float]) -> tuple[dict[str, bool], dict[str, float]]:
        if not states['game_window']:
            return (states, dimensions)

        window = Window()

        imgui.set_next_window_position(dimensions['left_window_width'], dimensions['main_menu_height'])
        imgui.set_next_window_size(
            window.width - dimensions['left_window_width'] - dimensions['right_window_width'],
            window.height - dimensions['main_menu_height'] - dimensions['bottom_window_height'],
        )

        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0.0, 0.0))
        _, states['game_window'] = imgui.begin(
            'game_window',
            flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_BRING_TO_FRONT_ON_FOCUS,
        )
        # Using a Child allow to fill all the space of the window.
        # It also alows customization
        imgui.begin_child('GameRender')
        # Get the size of the child (i.e. the whole draw size of the windows).
        wsize = imgui.get_window_size()

        if wsize.x != self.width or wsize.y != self.height:
            self._game_window_resize(wsize.x, wsize.y)

        # Because I use the texture from OpenGL, I need to invert the V from the UV.

        imgui.image(RasterRenderer().last_front_frame, wsize.x, wsize.y, (0, 1), (1, 0))

        self.crosshair.draw()

        imgui.end_child()

        imgui.pop_style_var()
        imgui.end()

        return states

    def _game_window_resize(self, width: int, height: int) -> None:
        int_width = int(width)
        int_height = int(height)

        glViewport(0, 0, int_width, int_height)
        RendererManager().update_dimensions(int_width, int_height)
        self.width = int_width
        self.height = int_height
