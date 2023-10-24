#version 330 core

layout(location = 0) in vec3 vertex;
layout(location = 2) in vec2 uv;

uniform int samples;

out vec2 frag_uv;
flat out int frag_samples;

void main() {
    gl_Position = vec4(vertex.x, vertex.y, vertex.z, 1.0); 
    frag_uv = uv;
    frag_samples = samples;
}