import imgui

from renderer.renderer_manager.renderer_manager import RendererManager


class MaterialTab:
    def __init__(self):
        self.selection_materials = {}
        self.selected_material = ""

    def draw(self):
        rm = RendererManager()
        wsize = imgui.get_window_size()
        list_box_size = (wsize.x / 3, wsize.y - 30)

        if imgui.begin_list_box("###materials_listbox", *list_box_size).opened:
            for material in rm.materials.keys():
                if material != self.selected_material:
                    self.selection_materials[material] = False
                else:
                    self.selection_materials[material] = True

                _, self.selection_materials[material] = imgui.selectable(
                    material, self.selection_materials[material]
                )

                if self.selection_materials[material] == True:
                    self.selected_material = material

            imgui.end_list_box()

        if len(self.selected_material) != 0:
            imgui.same_line()
            imgui.begin_child("material_child")
            imgui.push_item_width(
                imgui.get_content_region_available_width()
                - imgui.calc_text_size("Shininess").x
                - 16
            )

            material = rm.materials[self.selected_material]

            changed, ambient = imgui.color_edit3(
                "Ambient", material.ambient[0], material.ambient[1], material.ambient[2]
            )
            if changed:
                rm.set_ambient(self.selected_material, *ambient)

            changed, diffuse = imgui.color_edit3(
                "Diffuse", material.diffuse[0], material.diffuse[1], material.diffuse[2]
            )
            if changed:
                rm.set_diffuse(self.selected_material, *diffuse)

            changed, specular = imgui.color_edit3(
                "Specular",
                material.specular[0],
                material.specular[1],
                material.specular[2],
            )
            if changed:
                rm.set_specular(self.selected_material, *specular)

            changed, shininess = imgui.drag_float(
                "Shininess", material.shininess, change_speed=0.1
            )
            if changed:
                rm.set_shininess(self.selected_material, shininess)

            changed, roughness = imgui.drag_float(
                "Roughness", material.roughness, change_speed=0.001
            )
            if changed:
                rm.set_roughness(self.selected_material, roughness)

            changed, metallic = imgui.drag_float(
                "Metallic", material.metallic, change_speed=0.001
            )
            if changed:
                rm.set_metallic(self.selected_material, metallic)

            imgui.pop_item_width()
            imgui.end_child()
