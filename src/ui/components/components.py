import imgui

from renderer.renderer_manager.renderer_manager import RendererManager


class Components:
    def draw(self, states: dict[str, bool], dimensions: dict[str, float], selected_model: str) -> dict[str, bool]:
        rm = RendererManager()

        states['right_window/components_header'], _ = imgui.collapsing_header('Components')

        if states['right_window/components_header']:
            imgui.indent()

            meshes = list(rm.vaos.keys())
            shaders = list(rm.shaders.keys())
            materials = list(rm.materials.keys())
            textures = list(rm.textures.keys())

            available_width = dimensions['right_window_width'] - dimensions['indent_size'] * 2

            imgui.push_item_width(available_width)

            imgui.text('Mesh')
            clicked, selected_mesh = imgui.combo('###combo_mesh', meshes.index(rm.models[selected_model].mesh), meshes)

            if clicked:
                rm.models[selected_model].mesh = meshes[selected_mesh]

            imgui.text('Shader')
            clicked, selected_shader = imgui.combo(
                '###combo_shader', shaders.index(rm.models[selected_model].shader), shaders
            )

            if clicked:
                rm.models[selected_model].shader = shaders[selected_shader]

            imgui.text('Material')
            clicked, selected_material = imgui.combo(
                '###combo_material', materials.index(rm.models[selected_model].material), materials
            )

            if clicked:
                rm.models[selected_model].material = materials[selected_material]

            imgui.text('Texture')
            clicked, selected_texture = imgui.combo(
                '###combo_texture', textures.index(rm.models[selected_model].texture), textures
            )

            if clicked:
                rm.models[selected_model].texture = textures[selected_texture]

            imgui.pop_item_width()

            imgui.unindent()

        return states
