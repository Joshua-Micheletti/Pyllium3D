# version 330

layout(location = 0) in vec3 vertex;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec2 uv;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 frag_position;
out vec3 frag_normal;

void main() {
    mat4 mvp = projection * view * model;
    gl_Position = mvp * vec4(vertex, 1.0);
    frag_position = vec3(model * vec4(vertex, 1.0));
    frag_normal = mat3(transpose(inverse(model))) * normal;
}