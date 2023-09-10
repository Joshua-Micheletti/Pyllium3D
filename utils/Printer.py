import os
import platform

from utils.Singleton import Singleton
from utils.colors import colors
from utils.Timer import Timer

from renderer.RendererManager import RendererManager

class Printer(metaclass=Singleton):
    def __init__(self, interval = 2000):
        self.interval = interval
        self.frames_count = 3

        self._timer = Timer()
        self._frametimes = []
        
        if platform.system() == "Linux":
            self._clear_command = "clear"
        elif platform.system() == "Window":
            self._clear_command = "clr"

        self._print_string = ''

    def write(self, verbose = False, frametime=0.0):
        if self._timer.elapsed() > self.interval:
            self._prepare_data(frametime)

            os.system(self._clear_command)

            self._write_frametime(verbose)
            self._separator()
            self._write_vertices(verbose)
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

    def _write_frametime(self, verbose):
        frametime_text = "Ft"
        rounding = 0

        if verbose:
            frametime_text = "Frametime"
            rounding = 2
            self._print_string = "===================================\n"
        else:
            self._print_string = "========================\n"

        for i in range(len(self._frametimes)):
            fps = round(1000 / self._frametimes[i], rounding)
            frametime = self._frametimes[i]

            if rounding == 0:
                fps = int(fps)
                frametime = int(frametime)
            
            frametime_spaces = ''
            fps_spaces = ''

            for j in range((5 + rounding) - len(str(frametime))):
                frametime_spaces = frametime_spaces + ' '

            for j in range((5 + rounding) - len(str(fps))):
                fps_spaces = fps_spaces + ' '

            
            self._print_string += "| " + frametime_text + ": " + str(frametime) + frametime_spaces
            self._print_string += "| FPS: " + str(fps) + fps_spaces + "|"

            if i < len(self._frametimes) - 1:
                self._print_string += '\n'

    def _write_vertices(self, verbose):
        vertices_text = "V"
        triangles_text = "T"
        meshes_text = "M"

        if verbose:
            vertices_text = "Vertices"
            triangles_text = "Triangles"
            meshes_text = "Meshes"

        vertices_count = 0
        meshes = 0

        for key, value in RendererManager().vertices_count.items():
            vertices_count += int(value)
            meshes += 1

        self._print_string += "| " + vertices_text + ": " + str(vertices_count) + " |"
        self._print_string += " " + triangles_text + ": " + str(int(vertices_count / 3)) + " |"
        self._print_string += " " + meshes_text + ": " + str(meshes) + " |"

    def _separator(self):
        substrings = self._print_string.splitlines()
        
        if len(substrings) == 0:
            return
        
        last_string = substrings[len(substrings) - 1]

        separator = ''

        for i in range(len(last_string)):
            separator += '='

        self._print_string += '\n' + separator + '\n'