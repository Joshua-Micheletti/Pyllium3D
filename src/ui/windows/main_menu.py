import imgui
from renderer.RendererManager import RendererManager

class MainMenu:
    def __init__(self):
        self.height = 0
        self.width = 0

    def draw(self, states, dimensions):
        if imgui.begin_main_menu_bar():
            rm = RendererManager()
            wsize = imgui.get_window_size()
            dimensions["main_menu_height"] = wsize.y
            self.height = wsize.y
            self.width = wsize.x

            if imgui.begin_menu("File"):
                imgui.text("uwu")
                imgui.end_menu()

            if imgui.begin_menu("View"):

                imgui.align_text_to_frame_padding()
                imgui.text("Left window       ")
                imgui.same_line()
                _, states["left_window"] = imgui.checkbox("###left_window_checkbox", states["left_window"])

                imgui.align_text_to_frame_padding()
                imgui.text("Right window      ")
                imgui.same_line()
                _, states["right_window"] = imgui.checkbox("###right_window_checkbox", states["right_window"])

                imgui.align_text_to_frame_padding()
                imgui.text("Bottom window     ")
                imgui.same_line()
                _, states["bottom_window"] = imgui.checkbox("###bottom_window_checkbox", states["bottom_window"])

                imgui.align_text_to_frame_padding()
                imgui.text("Performance window")
                imgui.same_line()
                _, states["fps_window"] = imgui.checkbox("###fps_window_checkbox", states["fps_window"])

                imgui.end_menu()

            if imgui.begin_menu("Render"):
                imgui.align_text_to_frame_padding()
                imgui.text("Depth of field ")
                imgui.same_line()
                _, rm.render_states["depth_of_field"] = imgui.checkbox("###depth_of_field_checkbox", rm.render_states["depth_of_field"])

                imgui.align_text_to_frame_padding()
                imgui.text("Post processing")
                imgui.same_line()
                _, rm.render_states["post_processing"] = imgui.checkbox("###post_processing_checkbox", rm.render_states["post_processing"])

                imgui.end_menu()

            imgui.end_main_menu_bar()

        return(states, dimensions)