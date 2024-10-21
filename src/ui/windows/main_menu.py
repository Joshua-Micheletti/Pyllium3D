from imgui_bundle import imgui

from renderer.renderer_manager.renderer_manager import RendererManager


class MainMenu:
    def __init__(self) -> None:
        self.height = 0
        self.width = 0

    def draw(self, states: dict[str, bool], dimensions: dict[str, float]) -> tuple[dict[str, bool], dict[str, float]]:
        if imgui.begin_main_menu_bar():
            rm = RendererManager()
            wsize = imgui.get_window_size()
            dimensions['main_menu_height'] = wsize.y
            self.height = wsize.y
            self.width = wsize.x

            if imgui.begin_menu('File'):
                imgui.text('uwu')
                imgui.end_menu()

            if imgui.begin_menu('View'):
                imgui.align_text_to_frame_padding()
                imgui.text('Left window       ')
                imgui.same_line()
                _, states['left_window'] = imgui.checkbox('###left_window_checkbox', states['left_window'])

                imgui.align_text_to_frame_padding()
                imgui.text('Right window      ')
                imgui.same_line()
                _, states['right_window'] = imgui.checkbox('###right_window_checkbox', states['right_window'])

                imgui.align_text_to_frame_padding()
                imgui.text('Bottom window     ')
                imgui.same_line()
                _, states['bottom_window'] = imgui.checkbox('###bottom_window_checkbox', states['bottom_window'])

                imgui.align_text_to_frame_padding()
                imgui.text('Performance window')
                imgui.same_line()
                _, states['fps_window'] = imgui.checkbox('###fps_window_checkbox', states['fps_window'])

                imgui.end_menu()

            if imgui.begin_menu('Render'):
                imgui.align_text_to_frame_padding()
                imgui.text('Depth of field ')
                imgui.same_line()
                _, rm.render_states['depth_of_field'] = imgui.checkbox(
                    '###depth_of_field_checkbox', rm.render_states['depth_of_field']
                )

                imgui.align_text_to_frame_padding()
                imgui.text('Post processing')
                imgui.same_line()
                _, rm.render_states['post_processing'] = imgui.checkbox(
                    '###post_processing_checkbox', rm.render_states['post_processing']
                )

                imgui.align_text_to_frame_padding()
                imgui.text('Bloom          ')
                imgui.same_line()
                _, rm.render_states['bloom'] = imgui.checkbox('###bloom_checkbox', rm.render_states['bloom'])

                imgui.align_text_to_frame_padding()
                imgui.text('Shadows        ')
                imgui.same_line()
                _, rm.render_states['shadow_map'] = imgui.checkbox(
                    '###shadows_checkbox', rm.render_states['shadow_map']
                )

                imgui.align_text_to_frame_padding()
                imgui.text('MSAA')
                imgui.same_line()

                sample_values = []
                sample_values.append(str(rm.max_samples))

                for _ in range(rm.max_samples):
                    new_sample_value = int(sample_values[-1]) / 2

                    if int(new_sample_value) < 1:
                        break

                    sample_values.append(str(int(new_sample_value)))

                changed, sample_index = imgui.combo(
                    '###sample_combo',
                    sample_values.index(str(rm.samples)),
                    sample_values,
                )

                if changed:
                    rm.set_samples(int(sample_values[sample_index]))

                # _, rm.render_states["msaa"] = imgui.checkbox("###msaa_checkbox", rm.render_states["msaa"])

                imgui.end_menu()

            imgui.end_main_menu_bar()

        return (states, dimensions)
