#version 330 core
layout (location = 0) in vec2 vertex;
layout (location = 2) in vec2 uv;

uniform float user_distance;
uniform float user_range;

out vec2 frag_uv;
out float frag_distance;
out float frag_range;

void main() {
    gl_Position = vec4(vertex.x, vertex.y, 0.0, 1.0); 
    frag_uv = uv;
    frag_distance = user_distance;
    frag_range = user_range;
}  