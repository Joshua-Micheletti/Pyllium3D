import imgui
from imgui.integrations.glfw import GlfwRenderer
from OpenGL.GL import *

from window.Window import Window
from utils.Singleton import Singleton
from renderer.RendererManager import RendererManager

# class to implement UI
class UI(metaclass=Singleton):
    # constructor method
    def __init__(self):
        # create an OpenGL context for imgui
        imgui.create_context()
        # implement the GLFW backend
        self.implementation = GlfwRenderer(Window().window, attach_callbacks = False)

        self._setup_style()

        self.states = dict()
        self.states["window"] = True
        self.states["game_window"] = True
        self.states["left_window"] = True
        self.states["right_window_model_header"] = True
        self.states["right_window"] = True
        self.states["bottom_window"] = True
        self.states["first_draw"] = True

        self.game_window_width = 640
        self.game_window_height = 480

        self.main_menu_height = 0
        self.left_window_width = 0
        self.right_window_width = 0
        self.bottom_window_height = 0

        self.selected_model_index = 0
        self.selected_model = ""
        
        
    

    def draw(self):
        self.implementation.process_inputs()

        imgui.new_frame()

        self._draw_main_menu()

        self._draw_game_window()

        self._draw_left_window()
        self._draw_right_window()
        self._draw_bottom_window()

        self.states["first_draw"] = False

        imgui.show_demo_window()

        imgui.render()

        self.implementation.render(imgui.get_draw_data())

    def _draw_main_menu(self):
        if imgui.begin_main_menu_bar():
            wsize = imgui.get_window_size()
            self.main_menu_height = wsize.y

            if imgui.begin_menu("File"):
                imgui.text("uwu")
                imgui.end_menu()

            imgui.end_main_menu_bar()

    def _draw_game_window(self):
        if self.states["game_window"] == False:
            return

        window = Window()

        imgui.set_next_window_position(self.left_window_width, self.main_menu_height)
        imgui.set_next_window_size(window.width - self.left_window_width - self.right_window_width,
                                   window.height - self.main_menu_height - self.bottom_window_height)

        _, self.states["game_window"] = imgui.begin("game_window", flags = imgui.WINDOW_NO_TITLE_BAR)
        # Using a Child allow to fill all the space of the window.
        # It also alows customization
        imgui.begin_child("GameRender")
        # Get the size of the child (i.e. the whole draw size of the windows).
        wsize = imgui.get_window_size()

        if wsize.x != self.game_window_width or wsize.y != self.game_window_height:
            self._game_window_resize(wsize.x, wsize.y)
            
        # Because I use the texture from OpenGL, I need to invert the V from the UV.
        imgui.image(RendererManager().color_render_texture, wsize.x, wsize.y, (0, 1), (1, 0))
        imgui.end_child()
        imgui.end()

    def _game_window_resize(self, width, height):
        int_width = int(width)
        int_height = int(height)

        glViewport(0, 0, int_width, int_height)
        RendererManager().update_dimensions(int_width, int_height)
        self.game_window_width = int_width
        self.game_window_height = int_height

    def _draw_left_window(self):
        if self.states["left_window"] == False:
            return
        
        window = Window()

        imgui.set_next_window_position(0, self.main_menu_height)
        imgui.set_next_window_size_constraints((100, window.height - self.main_menu_height), (window.width / 2, window.height - self.main_menu_height))

        if self.states["first_draw"]:
            imgui.set_next_window_size(window.width / 6, window.height - self.main_menu_height)
        
        
        _, self.states["left_window"] = imgui.begin("left_window", flags = imgui.WINDOW_NO_TITLE_BAR)

        wsize = imgui.get_window_size()
        self.left_window_width = wsize.x

        imgui.text("Hellow!")

        imgui.end()

    def _draw_right_window(self):
        if self.states["right_window"] == False:
            return
        
        window = Window()
        rm = RendererManager()

        imgui.set_next_window_position(window.width, self.main_menu_height, pivot_x = 1.0)
        imgui.set_next_window_size_constraints((100, window.height - self.main_menu_height), (window.width / 2, window.height - self.main_menu_height))

        if self.states["first_draw"]:
            imgui.set_next_window_size(window.width / 6, window.height - self.main_menu_height)

        
        _, self.states["right_window"] = imgui.begin("right_window", flags = imgui.WINDOW_NO_TITLE_BAR)

        wsize = imgui.get_window_size()
        self.right_window_width = wsize.x


        self.states["right_window_model_header"], _ = imgui.collapsing_header("Model")

        if self.states["right_window_model_header"]:
            models = list(rm.models.keys())

            clicked, self.selected_model_index = imgui.combo("", self.selected_model_index, models)
            
            if clicked:
                self.selected_model = models[self.selected_model_index]


        if len(self.selected_model) != 0:
            self.states["right_window_transformation_header"], _ = imgui.collapsing_header("Transformation")

            if self.states["right_window_transformation_header"]:
                position = rm.positions[self.selected_model]
                rotation = rm.rotations[self.selected_model]
                scale = rm.scales[self.selected_model]
                imgui.push_item_width(self.right_window_width / 5)
                imgui.text("Position:")
                imgui.same_line()
                changed, x = imgui.drag_float("###p.x", position.x, change_speed = 0.1)
                imgui.same_line()
                changed, y = imgui.drag_float("###p.y", position.y, change_speed = 0.1)
                imgui.same_line()
                changed, z = imgui.drag_float("###p.z", position.z, change_speed = 0.1)
                rm.place(self.selected_model, x, y, z)

                imgui.text("Rotation:")
                imgui.same_line()
                changed, x = imgui.drag_float("###r.x", rotation.x)
                imgui.same_line()
                changed, y = imgui.drag_float("###r.y", rotation.y)
                imgui.same_line()
                changed, z = imgui.drag_float("###r.z", rotation.z)
                rm.rotate(self.selected_model, x, y, z)

                imgui.text("Scale:")
                imgui.same_line()
                changed, x = imgui.drag_float("###s.x", scale.x, change_speed = 0.1)
                imgui.same_line()
                changed, y = imgui.drag_float("###s.y", scale.y, change_speed = 0.1)
                imgui.same_line()
                changed, z = imgui.drag_float("###s.z", scale.z, change_speed = 0.1)
                rm.scale(self.selected_model, x, y, z)
                imgui.pop_item_width()

        imgui.end()

    def _draw_bottom_window(self):
        if self.states["bottom_window"] == False:
            return
        
        window = Window()
        
        imgui.set_next_window_position(self.left_window_width, window.height, pivot_y = 1.0)
        imgui.set_next_window_size_constraints((window.width - self.left_window_width - self.right_window_width, 100),
                                               (window.width - self.left_window_width - self.right_window_width, window.height / 2))

        if self.states["first_draw"]:
            imgui.set_next_window_size(window.width - self.left_window_width - self.right_window_width,
                                       window.height / 6)

        _, self.states["bottom_window"] = imgui.begin("bottom_window", flags = imgui.WINDOW_NO_TITLE_BAR)

        wsize = imgui.get_window_size()
        self.bottom_window_height = wsize.y

        imgui.text("bottom window")

        imgui.end()


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

