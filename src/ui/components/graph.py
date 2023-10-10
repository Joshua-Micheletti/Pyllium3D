import imgui
from array import array

class Graph:
    def __init__(self, name, samples = 90, scale_min = 0, scale_max = 300):
        self.name = name
        self.samples = samples
        self.graph_values = []
        self.scale_min = scale_min
        self.scale_max = scale_max

    def draw(self, dt):
        if len(self.graph_values) == 90:
            self.graph_values.pop(0)
                
        self.graph_values.append(dt)

        last_values = []

        if len(self.graph_values) < 6:
            average_value = sum(self.graph_values) / len(self.graph_values)
        else:
            for i in range(5):
                last_values.append(self.graph_values[-(i + 1)])

            average_value = sum(last_values) / len(last_values)

        av_size = imgui.get_content_region_available()

        graph_size = (av_size.x - imgui.calc_text_size(self.name).x - imgui.calc_text_size(str(round(average_value, 1))).x - 16, 20)

        plot_values = array('f', self.graph_values)
        imgui.align_text_to_frame_padding()
        imgui.text(self.name)
        imgui.same_line()
        imgui.plot_lines("###" + self.name + "_plot", plot_values, graph_size = graph_size, scale_min = self.scale_min, scale_max = self.scale_max)
        imgui.same_line()
        imgui.text(str(round(average_value, 1)))