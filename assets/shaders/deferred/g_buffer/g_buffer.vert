#version 330 core

layout (location = 0) in vec3 vertex;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec2 uv;

out vec3 frag_position;
out vec3 frag_normal;
out vec2 frag_uv;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    vec4 world_position = model * vec4(vertex, 1.0);
    frag_position = world_position.xyz;
    frag_uv = uv;

    mat3 normal_matrix = transpose(inverse(mat3(model)));
    frag_normal = normal_matrix * normal;

    gl_Position = projection * view * world_position;
}