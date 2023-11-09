#version 330 core
layout (location = 0) in vec3 vertex;
layout (location = 3) in mat4 model;

void main() {
    gl_Position = model * vec4(vertex, 1.0);
}  