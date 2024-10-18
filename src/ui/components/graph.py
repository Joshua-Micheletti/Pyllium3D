from array import array

import imgui
import imgui_bundle
from imgui_bundle import implot


class Graph:
    def __init__(self, name: str, samples: int = 90, scale_min: float = 0, scale_max: float = 60) -> None:
        self.name = name
        self.samples = samples
        self.graph_values = []
        self.graph_values_alt = []
        self.graph_values_sum = []
        self.scale_min = scale_min
        self.scale_max = scale_max

    def draw(self, dt: float, dt_alt: float = None) -> None:
        if len(self.graph_values) == 90:
            self.graph_values.pop(0)

        self.graph_values.append(dt)
        
        if dt_alt:
            dt_sum = dt + dt_alt
            
            if len(self.graph_values_alt) == 90:
                self.graph_values_alt.pop(0)
            self.graph_values_alt.append(dt_alt)
            
            if len(self.graph_values_sum) == 90:
                self.graph_values_sum.pop(0)
            self.graph_values_sum.append(dt_sum)

        last_values = []

        if len(self.graph_values) < 6:
            average_value = sum(self.graph_values if not dt_alt else self.graph_values_sum) / len(self.graph_values if not dt_alt else self.graph_values_sum)
        else:
            for i in range(5):
                last_values.append(self.graph_values[-(i + 1)] if not dt_alt else self.graph_values_sum[-(i + 1)])

            average_value = sum(last_values) / len(last_values)

        av_size = imgui.get_content_region_available()

        graph_size = (
            av_size.x - imgui.calc_text_size(self.name).x - imgui.calc_text_size(str(round(average_value, 1))).x - 16,
            20,
        )

        plot_values = array('f', self.graph_values)
        if dt_alt:
            plot_values_alt = array('f', self.graph_values_alt)
            plot_values_sum = array('f', self.graph_values_sum)
            
        imgui.align_text_to_frame_padding()
        imgui.text(self.name)
        imgui.same_line()
        
        if implot.begin_plot("Multiple Lines Plot"):
            # Plot the first line (Sine)
            implot.plot_line('###' + self.name + '_plot', plot_values)
            # Plot the second line (Cosine)
            implot.plot_line('###' + self.name + '_plot_cpu', plot_values_alt)
            implot.end_plot()
        # imgui.plot_lines(
        #     '###' + self.name + '_plot',
        #     plot_values,
        #     graph_size=graph_size,
        #     scale_min=self.scale_min,
        #     scale_max=self.scale_max,
        # )
        imgui.same_line()
        imgui.text(str(round(average_value, 1)))
