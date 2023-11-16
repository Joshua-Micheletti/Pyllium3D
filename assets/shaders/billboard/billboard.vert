#version 330

layout(location = 0) in vec3 vertex;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    vec3 camera_right = vec3(view[0][0], view[1][0], view[2][0]);
    vec3 camera_up = vec3(view[0][1], view[1][1], view[2][1]);
    vec3 position = vec3(model[3][0], model[3][1], model[3][2]);

    vec4 world_position = projection * view * vec4(position + camera_right * vertex.x + camera_up * vertex.y, 1.0);

    gl_Position = world_position;
}