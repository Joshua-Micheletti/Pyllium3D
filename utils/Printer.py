import os

from utils.Singleton import Singleton
from utils.colors import colors
from utils.Timer import Timer

from renderer.RendererManager import RendererManager

class Printer(metaclass=Singleton):
    def __init__(self, interval = 2000):
        self.inteval = interval
        self.frames_count = 3

        self._timer = Timer()
        self._frametimes = []
        
        self._print_string = ''

    def write(self, frametime=0.0):
        if self._timer.elapsed() > 2000:
            self._prepare_data(frametime)

            os.system("clear")

            self._write_frametime()
            self._separator()
            self._write_vertices()
            self._separator()

            print(self._print_string)
            self._print_string = ''
            
            self._timer.reset()


    def _prepare_data(self, frametime):
        if len(self._frametimes) < self.frames_count:
            self._frametimes.append(round(frametime, 2))
        else:
            self._frametimes.pop(0)
            self._frametimes.append(round(frametime, 2))

    def _write_frametime(self):
        for i in range(len(self._frametimes)):
            fps = round(1000 / self._frametimes[i], 2)
            
            frametime_spaces = ''
            fps_spaces = ''

            for j in range(8 - len(str(self._frametimes[i]))):
                frametime_spaces = frametime_spaces + ' '

            for j in range(8 - len(str(fps))):
                fps_spaces = fps_spaces + ' '

            self._print_string += "| Frametime: " + str(self._frametimes[i]) + frametime_spaces
            self._print_string += "| FPS: " + str(fps) + fps_spaces + "|"

            if i < len(self._frametimes) - 1:
                self._print_string += '\n'

    def _write_vertices(self):
        vertices_count = 0

        for key, value in RendererManager().vertices_count.items():
            vertices_count += int(value)

        self._print_string += "| Vertices: " + str(vertices_count) + " |"

    def _separator(self):
        substrings = self._print_string.splitlines()
        
        if len(substrings) == 0:
            return
        
        last_string = substrings[len(substrings) - 1]

        separator = ''

        for i in range(len(last_string)):
            separator += '='

        self._print_string += '\n' + separator + '\n'