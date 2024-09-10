import imgui

from renderer.renderer_manager.renderer_manager import RendererManager
from ui.components import MaterialTab, MeshTab, ShaderTab, TextureTab
from ui.windows.resizable_window import ResizableWindow
from window import Window


class BottomWindow(ResizableWindow):
    def __init__(self):
        super().__init__('up')

        self.width = 0
        self.height = 0

        self.selection_shaders = dict()
        self.selected_shader = ''
        self.mesh_tab = MeshTab()
        self.material_tab = MaterialTab()
        self.shader_tab = ShaderTab()
        self.texture_tab = TextureTab()

    def draw(self, states, dimensions):
        if states['bottom_window'] == False:
            dimensions['bottom_window_height'] = 0
            return (states, dimensions)

        window = Window()
        rm = RendererManager()

        imgui.set_next_window_position(dimensions['left_window_width'], window.height, pivot_y=1.0)
        imgui.set_next_window_size(self.width, self.height)
        imgui.set_next_window_size_constraints(
            (window.width - dimensions['left_window_width'] - dimensions['right_window_width'], 100),
            (window.width - dimensions['left_window_width'] - dimensions['right_window_width'], window.height / 2),
        )

        if states['first_draw']:
            imgui.set_next_window_size(
                window.width - dimensions['left_window_width'] - dimensions['right_window_width'], window.height / 6
            )

        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0.0, 0.0))

        _, states['bottom_window'] = imgui.begin(
            'bottom_window', flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE
        )

        wsize = imgui.get_window_size()
        dimensions['bottom_window_height'] = wsize.y

        self.width = wsize.x
        self.height = wsize.y

        # imgui.text("bottom window")
        if imgui.begin_tab_bar('bottom_window/tabs'):
            if imgui.begin_tab_item('Meshes').selected:
                self.mesh_tab.draw()
                imgui.end_tab_item()

            if imgui.begin_tab_item('Materials').selected:
                self.material_tab.draw()
                imgui.end_tab_item()

            if imgui.begin_tab_item('Shaders').selected:
                self.shader_tab.draw()
                imgui.end_tab_item()

            if imgui.begin_tab_item('Textures').selected:
                self.texture_tab.draw()
                imgui.end_tab_item()

            imgui.end_tab_bar()

        self.handle_resize()

        imgui.pop_style_var()
        imgui.end()

        return (states, dimensions)
