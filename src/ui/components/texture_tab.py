import imgui
from OpenGL.GL import *

from renderer.raster_renderer.raster_renderer import RasterRenderer
from renderer.renderer_manager.renderer_manager import RendererManager


class TextureTab:
    def __init__(self) -> None:
        pass

    def draw(self) -> None:
        rm = RendererManager()
        rr = RasterRenderer()
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
        # imgui.image(rm.solved_texture, texture_width, texture_height, (0, 1), (1, 0))
        # with imgui.begin("Blurred texture"):
        imgui.image(rr._blur_renderer.output_texture, texture_width, texture_height, (0, 1), (1, 0))
        # if imgui.is_item_hovered():
        #     self._image_tooltip(rr._blur_renderer.output_texture, texture_width, texture_height)
        imgui.same_line()
        # imgui.image(rm.blurred_texture, texture_width, texture_height, (0, 1), (1, 0))
        imgui.image(rr._bloom_renderer._bloom_mips[0], texture_width, texture_height, (0, 1), (1, 0))
        # if imgui.is_item_hovered():
        #     self._image_tooltip(rr._blur_renderer.output_texture, texture_width, texture_height)
        imgui.same_line()
        imgui.image(rr._deferred_renderer._output_depth, texture_width, texture_height, (0, 1), (1, 0))
        # if imgui.is_item_hovered():
        #     self._image_tooltip(rr._blur_renderer.output_texture, texture_width, texture_height)

        imgui.image(rr._deferred_renderer._position_texture, texture_width, texture_height, (0, 1), (1, 0))
        # if imgui.is_item_hovered():
        #     self._image_tooltip(rr._blur_renderer.output_texture, texture_width, texture_height)
        imgui.same_line()
        imgui.image(rr._deferred_renderer._normal_texture, texture_width, texture_height, (0, 1), (1, 0))
        # if imgui.is_item_hovered():
        #     self._image_tooltip(rr._blur_renderer.output_texture, texture_width, texture_height)
        imgui.same_line()
        imgui.image(rr._deferred_renderer._color_texture, texture_width, texture_height, (0, 1), (1, 0))
        # if imgui.is_item_hovered():
        #     self._image_tooltip(rr._blur_renderer.output_texture, texture_width, texture_height)

        imgui.image(rr._deferred_renderer._pbr_texture, texture_width, texture_height, (0, 1), (1, 0))
        # if imgui.is_item_hovered():
        #     self._image_tooltip(rr._blur_renderer.output_texture, texture_width, texture_height)

    def _image_tooltip(self, texture_id, tex_w, tex_h):
        with imgui.begin_tooltip():
            io = imgui.get_io()
            pos = imgui.get_cursor_screen_pos()
            region_sz: float = 32.0
            region_x: float = io.mouse_pos.x - pos.x - region_sz * 0.5
            region_y: float = io.mouse_pos.y - pos.y - region_sz * 0.5
            print(io.mouse_pos.x, io.mouse_pos.y)
            print(pos)
            zoom: float = 4.0
            if region_x < 0.0:
                region_x = 0.0
            elif region_x > tex_w - region_sz:
                region_x = tex_w - region_sz
            if region_y < 0.0:
                region_y = 0.0
            elif region_y > tex_h - region_sz:
                region_y = tex_h - region_sz

            imgui.text(f'Min: ({region_x}, {region_y})')
            # imgui.text("Max: (%.2f, %.2f)", region_x + region_sz, region_y + region_sz);
            uv0: tuple[float, float] = ((region_x) / tex_w, (region_y) / tex_h)
            uv1: tuple[float, float] = ((region_x + region_sz) / tex_w, (region_y + region_sz) / tex_h)
            imgui.image(texture_id, region_sz * zoom, region_sz * zoom, uv0, uv1)
