import imgui
from imgui.integrations.glfw import GlfwRenderer
from OpenGL.GL import *
import glm

from window.Window import Window
from utils.Singleton import Singleton
from renderer.RendererManager import RendererManager
from utils.colors import gui_colors

# class to implement UI
class UI(metaclass=Singleton):
    # constructor method
    def __init__(self):
        # create an OpenGL context for imgui
        imgui.create_context()
        # implement the GLFW backend
        self.implementation = GlfwRenderer(Window().window, attach_callbacks = False)

        self.indent_size = 8
        self._setup_style()

        self.font = None
        self._setup_font()

        self.states = dict()
        self.states["window"] = True
        self.states["game_window"] = True
        self.states["left_window"] = True
        self.states["right_window/model_header"] = True
        self.states["right_window/transformation_header"] = True
        self.states["right_window/components_header"] = True
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

        self.selected_shaders = []
        self.selection_meshes = dict()
        self.selected_mesh = ""
        self.selection_materials = dict()
        self.selected_material = ""

    def draw(self):
        self.implementation.process_inputs()

        imgui.new_frame()

        # imgui.font(self.font)
        imgui.push_font(self.font)

        self._draw_main_menu()

        self._draw_game_window()

        self._draw_left_window()
        self._draw_right_window()
        self._draw_bottom_window()

        imgui.show_demo_window()

        imgui.pop_font()

        self.states["first_draw"] = False

        imgui.render()

        self.implementation.render(imgui.get_draw_data())

    def _draw_main_menu(self):
        if imgui.begin_main_menu_bar():
            wsize = imgui.get_window_size()
            self.main_menu_height = wsize.y

            if imgui.begin_menu("File"):
                imgui.text("uwu")
                imgui.end_menu()

            if imgui.begin_menu("View"):
                imgui.align_text_to_frame_padding()
                imgui.text("Left window")
                imgui.same_line()
                _, self.states["left_window"] = imgui.checkbox("###left_window_checkbox", self.states["left_window"])

                imgui.align_text_to_frame_padding()
                imgui.text("Right window")
                imgui.same_line()
                _, self.states["right_window"] = imgui.checkbox("###right_window_checkbox", self.states["right_window"])

                imgui.align_text_to_frame_padding()
                imgui.text("Bottom window")
                imgui.same_line()
                _, self.states["bottom_window"] = imgui.checkbox("###bottom_window_checkbox", self.states["bottom_window"])

                imgui.end_menu()

            imgui.end_main_menu_bar()

    def _draw_game_window(self):
        if self.states["game_window"] == False:
            return

        window = Window()

        imgui.set_next_window_position(self.left_window_width, self.main_menu_height)
        imgui.set_next_window_size(window.width - self.left_window_width - self.right_window_width,
                                   window.height - self.main_menu_height - self.bottom_window_height)

        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0.0, 0.0))
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

        imgui.pop_style_var()
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
            self.left_window_width = 0
            return
        
        window = Window()

        imgui.set_next_window_position(0, self.main_menu_height)
        imgui.set_next_window_size_constraints((100, window.height - self.main_menu_height), (window.width / 2, window.height - self.main_menu_height))

        if self.states["first_draw"]:
            imgui.set_next_window_size(window.width / 6, window.height - self.main_menu_height)
        
        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0.0, 0.0))
        _, self.states["left_window"] = imgui.begin("left_window", flags = imgui.WINDOW_NO_TITLE_BAR)

        wsize = imgui.get_window_size()
        self.left_window_width = wsize.x

        imgui.text("Hellow!")

        imgui.pop_style_var()

        imgui.end()

    def _draw_right_window(self):
        if self.states["right_window"] == False:
            self.right_window_width = 0
            return
        
        window = Window()
        rm = RendererManager()

        imgui.set_next_window_position(window.width, self.main_menu_height, pivot_x = 1.0)
        imgui.set_next_window_size_constraints((100, window.height - self.main_menu_height), (window.width / 2, window.height - self.main_menu_height))

        if self.states["first_draw"]:
            imgui.set_next_window_size(window.width / 6, window.height - self.main_menu_height)

        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0.0, 0.0))
        _, self.states["right_window"] = imgui.begin("right_window", flags = imgui.WINDOW_NO_TITLE_BAR)

        wsize = imgui.get_window_size()
        self.right_window_width = wsize.x


        self.states["right_window/model_header"], _ = imgui.collapsing_header("Model")

        if self.states["right_window/model_header"]:
            imgui.indent()

            models = list(rm.models.keys())
            imgui.push_item_width(self.right_window_width - self.indent_size * 2)
            clicked, self.selected_model_index = imgui.combo("", self.selected_model_index, models)
            imgui.pop_item_width()
            
            if clicked:
                self.selected_model = models[self.selected_model_index]

            imgui.unindent()


        if len(self.selected_model) != 0:
            self.states["right_window/transformation_header"], _ = imgui.collapsing_header("Transformation")

            if self.states["right_window/transformation_header"]:
                imgui.indent()

                position = rm.positions[self.selected_model]
                rotation = rm.rotations[self.selected_model]
                scale = rm.scales[self.selected_model]

                item_spacing = 2.0
                normal_item_spacing = 8.0

                available_slider_width = self.right_window_width - \
                                         self.indent_size * 3 - \
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
            self.states["right_window/components_header"], _ = imgui.collapsing_header("Components")

            if self.states["right_window/components_header"]:
                imgui.indent()

                meshes = list(rm.vaos.keys())
                shaders = list(rm.shaders.keys())
                materials = list(rm.materials.keys())

                available_width = self.right_window_width - self.indent_size * 2

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

    def _draw_bottom_window(self):
        if self.states["bottom_window"] == False:
            self.bottom_window_height = 0
            return
        
        window = Window()
        rm = RendererManager()
        
        imgui.set_next_window_position(self.left_window_width, window.height, pivot_y = 1.0)
        imgui.set_next_window_size_constraints((window.width - self.left_window_width - self.right_window_width, 100),
                                               (window.width - self.left_window_width - self.right_window_width, window.height / 2))

        if self.states["first_draw"]:
            imgui.set_next_window_size(window.width - self.left_window_width - self.right_window_width,
                                       window.height / 6)

        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0.0, 0.0))

        _, self.states["bottom_window"] = imgui.begin("bottom_window", flags = imgui.WINDOW_NO_TITLE_BAR)

        wsize = imgui.get_window_size()
        self.bottom_window_height = wsize.y

        # imgui.text("bottom window")
        if imgui.begin_tab_bar("bottom_window/tabs"):
            if imgui.begin_tab_item("Meshes").selected:
                
                list_box_size = (wsize.x / 3, self.bottom_window_height - 30)

                if imgui.begin_list_box("###meshes_listbox", *list_box_size).opened:
                    for mesh in rm.vaos.keys():
                        if mesh != self.selected_mesh:
                            self.selection_meshes[mesh] = False
                        else:
                            self.selection_meshes[mesh] = True

                        _, self.selection_meshes[mesh] = imgui.selectable(mesh, self.selection_meshes[mesh])

                        if self.selection_meshes[mesh] == True:
                            self.selected_mesh = mesh


                    imgui.end_list_box()
                
                if len(self.selected_mesh) != 0:
                    vertices = rm.vertices_count[self.selected_mesh]
                    triangles = rm.vertices_count[self.selected_mesh] / 3

                    imgui.same_line()
                    imgui.text("Triangles: " + str(int(triangles)) + "\n" + "Vertices:  " + str(int(vertices)))

                imgui.end_tab_item()

            if imgui.begin_tab_item("Materials").selected:
                list_box_size = (wsize.x / 3, self.bottom_window_height - 30)

                if imgui.begin_list_box("###materials_listbox", *list_box_size).opened:
                    for material in rm.materials.keys():
                        if material != self.selected_material:
                            self.selection_materials[material] = False
                        else:
                            self.selection_materials[material] = True

                        _, self.selection_materials[material] = imgui.selectable(material, self.selection_materials[material])

                        if self.selection_materials[material] == True:
                            self.selected_material = material

                    imgui.end_list_box()

                if len(self.selected_material) != 0:
                    imgui.same_line()
                    imgui.push_item_width(wsize.x - list_box_size[0] - imgui.calc_text_size("Ambient").x - 16)
                    material = rm.materials[self.selected_material]
                    changed, ambient = imgui.color_edit3("Ambient", material["ambient"].x, material["ambient"].y, material["ambient"].z)

                    rm.materials[self.selected_material]["ambient"] = glm.vec3(ambient[0], ambient[1], ambient[2])

                    imgui.pop_item_width()


                    
                imgui.end_tab_item()

            if imgui.begin_tab_item("Shaders").selected:
                imgui.text("This is the Cucumber tab!\nblah blah blah blah blah")
                imgui.end_tab_item()
                
            imgui.end_tab_bar()

        imgui.pop_style_var()
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
        style.indent_spacing = self.indent_size

    def _setup_font(self):
        io = imgui.get_io()

        self.font = io.fonts.add_font_from_file_ttf("./assets/fonts/DroidSansMono/DroidSansMNerdFont-Regular.ttf", 14)
        self.implementation.refresh_font_texture()
        imgui.font(self.font)
