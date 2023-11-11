#version 330 core
layout (location = 0) in vec3 vertex;

out vec3 frag_position;

uniform mat4 projection;
uniform mat4 view;

void main() {
    frag_position = vertex;  
    gl_Position =  projection * view * vec4(vertex, 1.0);
}

