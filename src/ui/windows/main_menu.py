import imgui

class MainMenu:
    def __init__(self):
        self.height = 0
        self.width = 0

    def draw(self, states, dimensions):
        if imgui.begin_main_menu_bar():
            wsize = imgui.get_window_size()
            dimensions["main_menu_height"] = wsize.y
            self.height = wsize.y
            self.width = wsize.x

            if imgui.begin_menu("File"):
                imgui.text("uwu")
                imgui.end_menu()

            if imgui.begin_menu("View"):

                imgui.align_text_to_frame_padding()
                imgui.text("Left window  ")
                imgui.same_line()
                _, states["left_window"] = imgui.checkbox("###left_window_checkbox", states["left_window"])

                imgui.align_text_to_frame_padding()
                imgui.text("Right window ")
                imgui.same_line()
                _, states["right_window"] = imgui.checkbox("###right_window_checkbox", states["right_window"])

                imgui.align_text_to_frame_padding()
                imgui.text("Bottom window")
                imgui.same_line()
                _, states["bottom_window"] = imgui.checkbox("###bottom_window_checkbox", states["bottom_window"])

                imgui.end_menu()

            imgui.end_main_menu_bar()

        return(states, dimensions)