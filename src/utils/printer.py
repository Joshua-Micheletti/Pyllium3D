import os
import platform

from renderer.raster_renderer.raster_renderer import RasterRenderer
from renderer.renderer_manager.renderer_manager import RendererManager
from utils import Singleton, Timer


class Printer(metaclass=Singleton):
    def __init__(self, interval: int = 2000) -> None:
        self.interval = interval
        self.frames_count = 3

        self._timer = Timer()
        self._frametimes = []
        self._render_times = []
        self._other_times = []

        self._print_string = ''

    def write(self, verbose: bool = False, frametime: float = 0.0) -> None:
        if self._timer.elapsed() > self.interval:
            self._prepare_data(frametime)

            if platform.system() == 'Linux':
                os.system('clear')  # noqa: S605
            elif platform.system() == 'Window':
                os.system('cls')  # noqa: S605

            self._separator()
            self._write_vertices(verbose)
            self._separator()
            self._write_frametime(verbose)
            self._separator()

            self._fill_separators()

            print(self._print_string)

            self._print_string = ''

            self._timer.reset()

    def _prepare_data(self, frametime: float) -> None:
        if len(self._frametimes) == self.frames_count:
            self._frametimes.pop(0)
            self._render_times.pop(0)
            self._other_times.pop(0)

        self._frametimes.append(round(frametime, 2))
        self._render_times.append(round(sum(RasterRenderer().timer.laps) / len(RasterRenderer().timer.laps), 2))
        self._other_times.append(round(self._frametimes[-1] - self._render_times[-1], 2))

    def _write_frametime(self, verbose: bool) -> None:
        frametime_text = 'Ft'
        render_time_text = 'Rt'
        other_time_text = 'Ot'
        rounding = 0

        if verbose:
            frametime_text = 'Frametime'
            render_time_text = 'Render Time'
            other_time_text = 'Other'
            rounding = 2

        for i in range(len(self._frametimes)):
            fps = round(1000 / self._frametimes[i], rounding)
            frametime = self._frametimes[i]
            render_time = self._render_times[i]
            other_time = self._other_times[i]

            if rounding == 0:
                fps = int(fps)
                frametime = int(frametime)
                render_time = int(render_time)
                other_time = int(other_time)

            frametime_spaces = ''
            fps_spaces = ''
            render_time_spaces = ''
            other_time_spaces = ''

            for _ in range((5 + rounding) - len(str(frametime))):
                frametime_spaces = frametime_spaces + ' '
            for _ in range((5 + rounding) - len(str(fps))):
                fps_spaces = fps_spaces + ' '
            for _ in range((5 + rounding) - len(str(render_time))):
                render_time_spaces = render_time_spaces + ' '
            for _ in range((5 + rounding) - len(str(other_time))):
                other_time_spaces = other_time_spaces + ' '

            self._print_string += '| FPS: ' + str(fps) + fps_spaces
            self._print_string += '| ' + frametime_text + ': ' + str(frametime) + frametime_spaces
            self._print_string += '| ' + render_time_text + ': ' + str(render_time) + render_time_spaces
            self._print_string += '| ' + other_time_text + ': ' + str(other_time) + other_time_spaces
            self._print_string += ' |'

            if i < len(self._frametimes) - 1:
                self._print_string += '\n'

    def _write_vertices(self, verbose: bool) -> None:
        vertices_text = 'V'
        triangles_text = 'T'
        meshes_text = 'M'

        if verbose:
            vertices_text = 'Vertices'
            triangles_text = 'Triangles'
            meshes_text = 'Meshes'

        vertices_count = 0
        meshes = 0

        # for key, value in RendererManager().vertices_count.items():
        #     vertices_count += int(value)
        # meshes += 1

        for _, model in RendererManager().models.items():
            vertices_count += int(RendererManager().vertices_count[model.mesh])
            meshes += 1

        self._print_string += '| ' + vertices_text + ': ' + str(vertices_count) + ' |'
        self._print_string += ' ' + triangles_text + ': ' + str(int(vertices_count / 3)) + ' |'
        self._print_string += ' ' + meshes_text + ': ' + str(meshes) + ' |'

    def _separator(self) -> None:
        self._print_string += 'separator'

    def _fill_separators(self) -> None:
        components = self._print_string.split('separator')
        self._print_string = ''

        for i in range(len(components)):
            if i == 0 or i == len(components) - 1:
                continue

            if i == 1 and len(components[0]) == 0:
                up_phrases = components[i].split('\n')
                down_phrases = components[i + 1].split('\n')

                for _ in range(len(up_phrases[0])):
                    self._print_string += '='

                self._print_string += '\n'
                self._print_string += components[i]
                self._print_string += '\n'

                if len(up_phrases[0]) > len(down_phrases[0]):
                    for _ in range(len(up_phrases[0])):
                        self._print_string += '='

                    self._print_string += '\n'
                    continue

                for _ in range(len(down_phrases[0])):
                    self._print_string += '='

                self._print_string += '\n'

                continue

            self._print_string += components[i] + '\n'

            up_phrases = components[i].split('\n')
            down_phrases = components[i + 1].split('\n')

            if len(up_phrases[0]) > len(down_phrases[0]):
                for _ in range(len(up_phrases[0])):
                    self._print_string += '='
                self._print_string += '\n'
                continue

            for _ in range(len(down_phrases[0])):
                self._print_string += '='

            self._print_string += '\n'
