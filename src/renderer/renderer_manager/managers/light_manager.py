def new_light(self, name, light_position, light_color, light_strength) -> None:
    # increase the light counter
    self.lights_count += 1

    # save the new light in the lights list
    self.lights[name] = self.lights_count - 1

    # add the new light's position
    self.light_positions.append(light_position[0])
    self.light_positions.append(light_position[1])
    self.light_positions.append(light_position[2])

    # add the new light's color
    self.light_colors.append(light_color[0])
    self.light_colors.append(light_color[1])
    self.light_colors.append(light_color[2])

    # add the new light's strength
    self.light_strengths.append(light_strength)
