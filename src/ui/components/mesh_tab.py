import imgui
from renderer.RendererManager import RendererManager

class MeshTab:
    def __init__(self):
        self.selection_meshes = dict()
        self.selected_mesh = ""

    def draw(self):
        rm = RendererManager()

        wsize = imgui.get_window_size()

        list_box_size = (wsize.x / 3, wsize.y - 30)

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