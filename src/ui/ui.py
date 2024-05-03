import imgui
from imgui.integrations.glfw import GlfwRenderer
from OpenGL.GL import *

from window import Window
from utils import Singleton
from utils import Timer

from ui.windows import MainMenu
from ui.windows import GameWindow
from ui.windows import LeftWindow
from ui.windows import RightWindow
from ui.windows import BottomWindow
from ui.windows import FpsWindow

# class to implement UI
class UI(metaclass=Singleton):
    # constructor method
    def __init__(self):
        window = Window()
        # create an OpenGL context for imgui
        imgui.create_context()
        # implement the GLFW backend
        self.implementation = GlfwRenderer(Window().window, attach_callbacks = False)

        # size of indentation
        self.dimensions = dict()
        self.dimensions["game_window_width"] = window.width
        self.dimensions["game_window_height"] = window.height
        self.dimensions["main_menu_height"] = 0
        self.dimensions["left_window_width"] = 0
        self.dimensions["right_window_width"] = 0
        self.dimensions["bottom_window_height"] = 0
        self.dimensions["indent_size"] = 8

        # setup the initial style of the UI
        self._setup_style()

        # set a font for the UI
        self.font = None
        self._setup_font()

        # create a dictionary to keep track of all the states of the UI
        self.states = dict()
        self.states["window"] = True
        self.states["game_window"] = True
        self.states["left_window"] = True
        self.states["right_window/model_header"] = True
        self.states["right_window/transformation_header"] = True
        self.states["right_window/components_header"] = True
        self.states["right_window/lights_header"] = True
        self.states["right_window"] = True
        self.states["bottom_window"] = True
        self.states["fps_window"] = True
        self.states["first_draw"] = True

        self.main_menu = MainMenu()
        self.game_window = GameWindow()
        self.left_window = LeftWindow()
        self.right_window = RightWindow()
        self.bottom_window = BottomWindow()
        self.fps_window = FpsWindow()

        self.timer = Timer()
        self.timer.record()

    def draw(self, dt, swaptime, controltime, updatetime, rmupdatetime):
        self.timer.reset()

        self.implementation.process_inputs()

        imgui.new_frame()

        imgui.push_font(self.font)

        
        self.states, self.dimensions = self.main_menu.draw(self.states, self.dimensions)
        self.states                  = self.game_window.draw(self.states, self.dimensions)        
        self.states, self.dimensions = self.left_window.draw(self.states, self.dimensions)       
        self.states, self.dimensions = self.right_window.draw(self.states, self.dimensions)        
        self.states, self.dimensions = self.bottom_window.draw(self.states, self.dimensions)
        self.states, self.dimensions = self.fps_window.draw(self.states, self.dimensions,
                                                            dt=dt, swaptime=swaptime,
                                                            controltime=controltime,
                                                            ui_time=self.timer.get_last_record(),
                                                            updatetime=updatetime,
                                                            rmupdatetime=rmupdatetime)

        # imgui.show_demo_window()

        imgui.pop_font()

        self.states["first_draw"] = False

        imgui.render()
        self.implementation.render(imgui.get_draw_data())

        self.timer.record()
        
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
        style.indent_spacing = self.dimensions["indent_size"]

    def _setup_font(self):
        io = imgui.get_io()

        self.font = io.fonts.add_font_from_file_ttf("./assets/fonts/DroidSansMono/DroidSansMNerdFont-Regular.ttf", 14)
        self.implementation.refresh_font_texture()
        imgui.font(self.font)
