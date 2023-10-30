import imgui

from renderer.renderer_manager import RendererManager

class ShaderTab:
    def __init__(self):
        self.selection_shaders = dict()
        self.selected_shader = ""

    def draw(self):
        rm = RendererManager()
        wsize = imgui.get_window_size()
        list_box_size = (wsize.x / 3, wsize.y - 30)

        if imgui.begin_list_box("###shaders_listbox", *list_box_size).opened:
            for shader in rm.shaders.keys():
                if shader != self.selected_shader:
                    self.selection_shaders[shader] = False
                else:
                    self.selection_shaders[shader] = True

                _, self.selection_shaders[shader] = imgui.selectable(shader, self.selection_shaders[shader])

                if self.selection_shaders[shader] == True:
                    self.selected_shader = shader

            imgui.end_list_box()

        if len(self.selected_shader) != 0:
            imgui.same_line()

            shader = rm.shaders[self.selected_shader]

            text = "Uniforms:"
            
            max_uniform_length = 0

            for key, value in shader.uniforms.items():
                if len(key) > max_uniform_length:
                    max_uniform_length = len(key)

            for key, value in shader.uniforms.items():
                spaces_count = max_uniform_length - len(key)

                spaces = " "

                for i in range(spaces_count):
                    spaces += " "

                text += "\n  "
                text += self._get_uniform_type(key) + " " + key + "" + spaces + str(value)

            imgui.begin_child("###shader_child")

            imgui.text(text)

            imgui.end_child()

    def _get_uniform_type(self, uniform):
        if uniform == "model" or \
           uniform == "view" or \
           uniform == "projection":
            return("mat4 ")
        
        if uniform == "light" or \
           uniform == "eye" or \
           uniform == "ambient" or \
           uniform == "diffuse" or \
           uniform == "specular" or \
           uniform == "light_ambient" or \
           uniform == "light_diffuse" or \
           uniform == "light_specular":
            return("vec3 ")

        if uniform == "shininess":
            return("float")
        
        return("?   ")