import imgui

from renderer.renderer_manager import RendererManager

class TextureTab:
    def __init__(self):
        pass

    def draw(self):
        rm = RendererManager()
        style = imgui.get_style()

        wsize = imgui.get_content_region_available()

        texture_ratio = rm.height / rm.width

        max_size = wsize.x / 3 - style.item_spacing.x / 2

        # if texture_ratio < 1:
            # width less than height, ratio = 0.n
        texture_width = max_size
        texture_height = max_size * texture_ratio
        # else:
            # width more than height, ratio = 1.n
            # texture_height = max_size
            # texture_width = max_size * texture_ratio

        imgui.image(rm.solved_texture, texture_width, texture_height, (0, 1), (1, 0))
        imgui.same_line()
        imgui.image(rm.blurred_texture, texture_width, texture_height, (0, 1), (1, 0))
        imgui.same_line()
        imgui.image(rm.solved_depth_texture, texture_width, texture_height, (0, 1), (1, 0))