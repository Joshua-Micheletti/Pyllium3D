import imgui
import glfw

from window import Window

class ResizableWindow:
    def __init__(self, direction: str) -> None:
        self.width: int = 0
        self.height: int = 0

        self.is_resizing: bool = False
        self.resize_start_pos: list[int] = [0, 0]
        self.resize_start_size: list[int] = [0, 0]

        self.resize_direction: str = direction

    def handle_resize(self) -> None:
        window: Window = Window()

        if imgui.is_window_hovered() and glfw.get_mouse_button(window.window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            if not self.is_resizing and self.is_mouse_pos_on_border():
                self.is_resizing = True
                self.resize_start_pos = glfw.get_cursor_pos(window.window)
                self.resize_start_size = [self.width, self.height]

        if self.is_resizing and glfw.get_mouse_button(window.window, glfw.MOUSE_BUTTON_LEFT) == glfw.RELEASE:
            self.is_resizing = False

        if self.is_resizing:
            mouse_x, mouse_y = glfw.get_cursor_pos(window.window)
            mouse_delta_x = mouse_x - self.resize_start_pos[0]
            mouse_delta_y = mouse_y - self.resize_start_pos[1]

            if self.resize_direction == 'right':
                self.width = self.resize_start_size[0] + mouse_delta_x
            elif self.resize_direction == 'left':
                self.width = self.resize_start_size[0] - mouse_delta_x
            elif self.resize_direction == 'up':
                self.height = self.resize_start_size[1] - mouse_delta_y
            elif self.resize_direction == 'down':
                self.height = self.resize_start_size[1] + mouse_delta_y
                
    def is_mouse_pos_on_border(self) -> bool:
        io: any = imgui.get_io()

        border_size: float = 8.0  # Adjust as needed

         # Check top border
        if io.mouse_pos.y - imgui.get_window_position()[1] < border_size:
            return(True)

        # Check bottom border
        if imgui.get_window_position()[1] + imgui.get_window_size()[1] - io.mouse_pos.y < border_size:
            return(True)

        # Check left border
        if io.mouse_pos.x - imgui.get_window_position()[0] < border_size:
            return(True)

        # Check right border
        if imgui.get_window_position()[0] + imgui.get_window_size()[0] - io.mouse_pos.x < border_size:
            return(True)

        return(False)