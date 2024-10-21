from imgui_bundle import imgui

from renderer.raster_renderer.raster_renderer import RasterRenderer
from renderer.renderer_manager.renderer_manager import RendererManager
from ui.components import Graph
from ui.windows.resizable_window import ResizableWindow
from window import Window


class FpsWindow(ResizableWindow):
    def __init__(self) -> None:
        super().__init__('down')

        self.fps_values = []
        self.frametime_values = []
        self.rendertime_values = []
        self.ui_time_values = []

        self.fps_graph = Graph('FPS:', scale_max=300)
        self.frametime_graph = Graph('Frametime: ')

        # self.rendertime_graph = Graph('Rendertime:')
        self.modeltimegraph = Graph('Models:    ', scale_max=10)
        self.instancetimegraph = Graph('Instances: ', scale_max=10)
        self.skyboxtimegraph = Graph('Skybox:    ', scale_max=10)
        self.msaatimegraph = Graph('MSAA:      ', scale_max=10)
        self.bloomtimegraph = Graph('Bloom:     ', scale_max=10)
        self.hdrtimegraph = Graph('Tonemap:   ', scale_max=10)
        self.blurtimegraph = Graph('Blur:      ', scale_max=10)
        self.doftimegraph = Graph('DOF:       ', scale_max=10)
        self.postproctimegraph = Graph('PostProc:  ', scale_max=10)
        self.shadowmaptimegraph = Graph('Shadow Map:', scale_max=10)
        self.othertimegraph = Graph('Other:     ', scale_max=10)

        self._render_graphs: dict[Graph]

        self.ui_time_graph = Graph('UI:        ')
        self.swaptime_graph = Graph('Swaptime:  ')
        self.control_graph = Graph('Control:   ')
        self.update_graph = Graph('Update:    ')
        self.rm_update_graph = Graph('RM Update: ')

        self._setup_graphs()

    def _setup_graphs(self):
        rr = RasterRenderer()

        self._render_graphs = {}

        for key in rr.timers:
            self._render_graphs[key] = Graph(f'{key}: ', scale_max=10)

    def draw(
        self,
        states: dict[str, bool],
        dimensions: dict[str, float],
        dt: float,
        ui_time: float,
        swaptime: float,
        controltime: float,
        updatetime: float,
        rmupdatetime: float,
    ) -> tuple[dict[str, bool], dict[str, float]]:
        if not states['fps_window']:
            return (states, dimensions)

        window = Window()
        renderer = RasterRenderer()

        imgui.set_next_window_position(
            window.width - dimensions['right_window_width'], dimensions['main_menu_height'], pivot_x=1.0
        )
        imgui.set_next_window_size(self.width, self.height)
        imgui.set_next_window_size_constraints(
            (200, 60), (window.width / 2, window.height / 2 - dimensions['main_menu_height'])
        )

        _, states['fps_window'] = imgui.begin('fps_window', flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE)

        self.fps_graph.draw(1000 / dt)

        states['fps_window/details_header'], _ = imgui.collapsing_header('Details')

        if states['fps_window/details_header']:
            self.frametime_graph.draw(dt)

            # total_render_time = renderer.timer.get_last_record()
            # self.rendertime_graph.draw(total_render_time)

            if RendererManager().render_states['profile']:
                for key, graph in self._render_graphs.items():
                    graph.draw(renderer.timers.get(key).get('gpu'))

                # remaining_time = total_render_time

                # for query in renderer.queries.values():
                #     remaining_time -= query.get('value')

                # self.othertimegraph.draw(remaining_time)

            self.ui_time_graph.draw(ui_time)
            self.swaptime_graph.draw(swaptime)
            self.control_graph.draw(controltime)
            self.update_graph.draw(updatetime)
            self.rm_update_graph.draw(rmupdatetime)

        self.handle_resize()

        imgui.end()

        return (states, dimensions)
