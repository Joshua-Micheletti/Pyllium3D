import imgui
from imgui.integrations.glfw import GlfwRenderer
from window.Window import Window

from utils.Singleton import Singleton
from renderer.RendererManager import RendererManager


class UI(metaclass=Singleton):
    def __init__(self):
        imgui.create_context()
        self.implementation = GlfwRenderer(Window().window, attach_callbacks = False)

        self._setup_style()

        self.states = dict()
        self.states["window"] = True
        self.states["game_window"] = True
        
    

    def draw(self):
        self.implementation.process_inputs()

        imgui.new_frame()

        if self.states["window"]:
            _, self.states["window"] = imgui.begin("window", closable=True)
            imgui.text("Hello world")
            imgui.end()

        if self.states["game_window"]:
            _, self.states["game_window"] = imgui.begin("game_window", closable=True)
            # Using a Child allow to fill all the space of the window.
            # It also alows customization
            imgui.begin_child("GameRender")
            # Get the size of the child (i.e. the whole draw size of the windows).
            wsize = imgui.get_window_size()
            print(wsize)
            # Because I use the texture from OpenGL, I need to invert the V from the UV.
            imgui.image(RendererManager().color_render_texture, wsize, imgui.Vec2(0, 1), imgui.Vec2(1, 0))
            imgui.end_child()
            imgui.end()

        # imgui.show_demo_window()

        imgui.render()

        self.implementation.render(imgui.get_draw_data())

    
    def _setup_style(self):
        style = imgui.get_style()
        style.colors[imgui.COLOR_TEXT]                         = (1.00, 1.00, 1.00, 1.00)
        style.colors[imgui.COLOR_TEXT_DISABLED]                = (0.50, 0.50, 0.50, 1.00)
        style.colors[imgui.COLOR_WINDOW_BACKGROUND]            = (0.13, 0.14, 0.15, 1.00)
        style.colors[imgui.COLOR_CHILD_BACKGROUND]             = (0.13, 0.14, 0.15, 1.00)
        style.colors[imgui.COLOR_POPUP_BACKGROUND]             = (0.13, 0.14, 0.15, 1.00)
        style.colors[imgui.COLOR_BORDER]                       = (0.43, 0.43, 0.50, 0.50)
        style.colors[imgui.COLOR_BORDER_SHADOW]                = (0.00, 0.00, 0.00, 0.00)
        style.colors[imgui.COLOR_FRAME_BACKGROUND]             = (0.25, 0.25, 0.25, 1.00)
        style.colors[imgui.COLOR_FRAME_BACKGROUND_HOVERED]     = (0.38, 0.38, 0.38, 1.00)
        style.colors[imgui.COLOR_FRAME_BACKGROUND_ACTIVE]      = (0.67, 0.67, 0.67, 0.39)
        style.colors[imgui.COLOR_TITLE_BACKGROUND]             = (0.08, 0.08, 0.09, 1.00)
        style.colors[imgui.COLOR_TITLE_BACKGROUND_ACTIVE]      = (0.08, 0.08, 0.09, 1.00)
        style.colors[imgui.COLOR_TITLE_BACKGROUND_COLLAPSED]   = (0.00, 0.00, 0.00, 0.51)
        style.colors[imgui.COLOR_MENUBAR_BACKGROUND]           = (0.14, 0.14, 0.14, 1.00)
        style.colors[imgui.COLOR_SCROLLBAR_BACKGROUND]         = (0.02, 0.02, 0.02, 0.53)
        style.colors[imgui.COLOR_SCROLLBAR_GRAB]               = (0.31, 0.31, 0.31, 1.00)
        style.colors[imgui.COLOR_SCROLLBAR_GRAB_HOVERED]       = (0.41, 0.41, 0.41, 1.00)
        style.colors[imgui.COLOR_SCROLLBAR_GRAB_ACTIVE]        = (0.51, 0.51, 0.51, 1.00)
        style.colors[imgui.COLOR_CHECK_MARK]                   = (0.11, 0.64, 0.92, 1.00)
        style.colors[imgui.COLOR_SLIDER_GRAB]                  = (0.11, 0.64, 0.92, 1.00)
        style.colors[imgui.COLOR_SLIDER_GRAB_ACTIVE]           = (0.08, 0.50, 0.72, 1.00)
        style.colors[imgui.COLOR_BUTTON]                       = (0.25, 0.25, 0.25, 1.00)
        style.colors[imgui.COLOR_BUTTON_HOVERED]               = (0.38, 0.38, 0.38, 1.00)
        style.colors[imgui.COLOR_BUTTON_ACTIVE]                = (0.67, 0.67, 0.67, 0.39)
        style.colors[imgui.COLOR_HEADER]                       = (0.22, 0.22, 0.22, 1.00)
        style.colors[imgui.COLOR_HEADER_HOVERED]               = (0.25, 0.25, 0.25, 1.00)
        style.colors[imgui.COLOR_HEADER_ACTIVE]                = (0.67, 0.67, 0.67, 0.39)
        style.colors[imgui.COLOR_SEPARATOR]                    = style.colors[imgui.COLOR_BORDER]
        style.colors[imgui.COLOR_SEPARATOR_HOVERED]            = (0.41, 0.42, 0.44, 1.00)
        style.colors[imgui.COLOR_SEPARATOR_ACTIVE]             = (0.26, 0.59, 0.98, 0.95)
        style.colors[imgui.COLOR_RESIZE_GRIP]                  = (0.00, 0.00, 0.00, 0.00)
        style.colors[imgui.COLOR_RESIZE_GRIP_HOVERED]          = (0.29, 0.30, 0.31, 0.67)
        style.colors[imgui.COLOR_RESIZE_GRIP_ACTIVE]           = (0.26, 0.59, 0.98, 0.95)
        style.colors[imgui.COLOR_TAB]                          = (0.08, 0.08, 0.09, 0.83)
        style.colors[imgui.COLOR_TAB_HOVERED]                  = (0.33, 0.34, 0.36, 0.83)
        style.colors[imgui.COLOR_TAB_ACTIVE]                   = (0.23, 0.23, 0.24, 1.00)
        style.colors[imgui.COLOR_TAB_UNFOCUSED]                = (0.08, 0.08, 0.09, 1.00)
        style.colors[imgui.COLOR_TAB_UNFOCUSED_ACTIVE]         = (0.13, 0.14, 0.15, 1.00)
        # style.colors[imgui.COLOR_ImGuiCol_DockingPreview]        = (0.26, 0.59, 0.98, 0.70)
        # style.colors[imgui.COLOR_ImGuiCol_DockingEmptyBg]        = (0.20, 0.20, 0.20, 1.00)
        style.colors[imgui.COLOR_PLOT_LINES]                   = (0.61, 0.61, 0.61, 1.00)
        style.colors[imgui.COLOR_PLOT_LINES_HOVERED]           = (1.00, 0.43, 0.35, 1.00)
        style.colors[imgui.COLOR_PLOT_HISTOGRAM]               = (0.90, 0.70, 0.00, 1.00)
        style.colors[imgui.COLOR_PLOT_HISTOGRAM_HOVERED]       = (1.00, 0.60, 0.00, 1.00)
        style.colors[imgui.COLOR_TEXT_SELECTED_BACKGROUND]     = (0.26, 0.59, 0.98, 0.35)
        style.colors[imgui.COLOR_DRAG_DROP_TARGET]             = (0.11, 0.64, 0.92, 1.00)
        style.colors[imgui.COLOR_NAV_HIGHLIGHT]                = (0.26, 0.59, 0.98, 1.00)
        style.colors[imgui.COLOR_NAV_WINDOWING_HIGHLIGHT]      = (0.80, 0.80, 0.80, 0.20)
        style.colors[imgui.COLOR_NAV_WINDOWING_DIM_BACKGROUND] = (0.80, 0.80, 0.80, 0.35)
        style.grab_rounding = style.frame_rounding = style.window_rounding = 2.3
        style.window_border_size = 0.0

