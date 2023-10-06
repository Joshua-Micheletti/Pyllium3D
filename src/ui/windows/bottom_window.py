import imgui
import glm

from window.Window import Window
from renderer.RendererManager import RendererManager

class BottomWindow:
    def __init__(self):
        self.width = 0
        self.height = 0

        self.selection_shaders = dict()
        self.selected_shader = ""
        self.selection_meshes = dict()
        self.selected_mesh = ""
        self.selection_materials = dict()
        self.selected_material = ""

    def draw(self, states, dimensions):
        if states["bottom_window"] == False:
            dimensions["bottom_window_height"] = 0
            return(states, dimensions)
        
        window = Window()
        rm = RendererManager()
        
        imgui.set_next_window_position(dimensions["left_window_width"], window.height, pivot_y = 1.0)
        imgui.set_next_window_size_constraints((window.width - dimensions["left_window_width"] - dimensions["right_window_width"], 100),
                                               (window.width - dimensions["left_window_width"] - dimensions["right_window_width"], window.height / 2))

        if states["first_draw"]:
            imgui.set_next_window_size(window.width - dimensions["left_window_width"] - dimensions["right_window_width"],
                                       window.height / 6)

        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0.0, 0.0))

        _, states["bottom_window"] = imgui.begin("bottom_window", flags = imgui.WINDOW_NO_TITLE_BAR)

        wsize = imgui.get_window_size()
        dimensions["bottom_window_height"] = wsize.y

        self.width = wsize.x
        self.height = wsize.y

        # imgui.text("bottom window")
        if imgui.begin_tab_bar("bottom_window/tabs"):
            if imgui.begin_tab_item("Meshes").selected:
                
                list_box_size = (wsize.x / 3, dimensions["bottom_window_height"] - 30)

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
                list_box_size = (wsize.x / 3, dimensions["bottom_window_height"] - 30)

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
                    imgui.begin_child("material_child")
                    imgui.push_item_width(imgui.get_content_region_available_width() - imgui.calc_text_size("Shininess").x - 16)
                    material = rm.materials[self.selected_material]

                    changed, ambient = imgui.color_edit3("Ambient", material["ambient"].x, material["ambient"].y, material["ambient"].z)
                    if changed:
                        rm.materials[self.selected_material]["ambient"] = glm.vec3(ambient[0], ambient[1], ambient[2])

                    changed, diffuse = imgui.color_edit3("Diffuse", material["diffuse"].x, material["diffuse"].y, material["diffuse"].z)
                    if changed:
                        rm.materials[self.selected_material]["diffuse"] = glm.vec3(diffuse[0], diffuse[1], diffuse[2])

                    changed, specular = imgui.color_edit3("Specular", material["specular"].x, material["specular"].y, material["specular"].z)
                    if changed:
                        rm.materials[self.selected_material]["specular"] = glm.vec3(specular[0], specular[1], specular[2])

                    changed, shininess = imgui.drag_float("Shininess", material["shininess"], change_speed = 0.1)
                    if changed:
                        rm.materials[self.selected_material]["shininess"] = shininess

                    imgui.pop_item_width()
                    imgui.end_child()
                    
                imgui.end_tab_item()

            if imgui.begin_tab_item("Shaders").selected:
                list_box_size = (wsize.x / 3, dimensions["bottom_window_height"] - 30)

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

                imgui.end_tab_item()
                
            imgui.end_tab_bar()

        imgui.pop_style_var()
        imgui.end()

        return(states, dimensions)
    
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
