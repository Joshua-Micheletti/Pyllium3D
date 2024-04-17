import imgui
import random

from window.window import Window
from renderer.renderer_manager import RendererManager

from ui.windows.resizable_window import ResizableWindow

class LeftWindow(ResizableWindow):
    def __init__(self):
        super().__init__('right')

        self.active_pp_shaders = []
        self.selected_pp_shader_index = 0
        self.selected_active_pp_shader = -1

    def draw(self, states, dimensions):
        if states["left_window"] == False:
            dimensions["left_window_width"] = 0
            return(states, dimensions)
        
        window = Window()
        rm = RendererManager()

        imgui.set_next_window_position(0, dimensions["main_menu_height"])
        imgui.set_next_window_size(self.width, self.height)
        
        imgui.set_next_window_size_constraints((100, window.height - dimensions["main_menu_height"]),
                                               (window.width / 2, window.height - dimensions["main_menu_height"]))

        if states["first_draw"]:
            imgui.set_next_window_size(window.width / 6, window.height - dimensions["main_menu_height"])
        
        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0.0, 0.0))
        _, states["left_window"] = imgui.begin("left_window", flags = imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE)

        wsize = imgui.get_window_size()
        dimensions["left_window_width"] = wsize.x
        self.width = wsize.x
        self.height = wsize.y

        states["left_window/post_processing_header"], _ = imgui.collapsing_header("Post Processing")

        changed = False

        if states["left_window/post_processing_header"]:
            imgui.indent()

            # pp_shaders = rm.available_post_processing_shaders
            pp_shaders = []
            for shader in rm.available_post_processing_shaders:
                components = shader.split('/')
                pp_shaders.append(components[1])

            clicked, self.selected_pp_shader_index = imgui.combo("###pp_shader", self.selected_pp_shader_index, pp_shaders)
            imgui.same_line()
             
            clicked = imgui.button("Add###add_pp_shader")

            if clicked and self.selected_pp_shader_index != None:
                self.active_pp_shaders.append(pp_shaders[self.selected_pp_shader_index] + '###' + str(random.random()))
                changed = True
                
            for i in range(len(self.active_pp_shaders)):
                _, selected = imgui.selectable(self.active_pp_shaders[i], self.selected_active_pp_shader == i)

                if selected:
                    self.selected_active_pp_shader = i

                if imgui.is_item_active() and not imgui.is_item_hovered():
                    next_index = i + (-1 if imgui.get_mouse_drag_delta(0).y < 0.0 else 1)

                    if next_index >= 0 and next_index < len(self.active_pp_shaders):
                        tmp = self.active_pp_shaders[i]
                        self.active_pp_shaders[i] = self.active_pp_shaders[next_index]
                        self.active_pp_shaders[next_index] = tmp
                        changed = True

            if self.selected_active_pp_shader != -1:
                if imgui.button("Remove###remove_pp_shader"):
                    self.active_pp_shaders.pop(self.selected_active_pp_shader)
                    self.selected_active_pp_shader = -1
                    changed = True
                else:
                    shader_name = "post_processing/" + self.active_pp_shaders[self.selected_active_pp_shader].split('###')[0]

                    for name, value in rm.shaders[shader_name].user_uniforms.items():
                        imgui.text(name)
                        imgui.same_line()
                        changed, new_value = imgui.drag_float("###" + name, value, change_speed = 0.1)

                        if changed:
                            rm.shaders[shader_name].user_uniforms[name] = new_value


        if changed:
            rm.post_processing_shaders = []
            
            for i in range(len(self.active_pp_shaders)):
                components = self.active_pp_shaders[i].split("###")
                rm.add_post_processing_shader('post_processing/' + components[0])

        self.handle_resize()

        imgui.pop_style_var()

        imgui.end()

        return(states, dimensions)

