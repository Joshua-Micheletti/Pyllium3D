#version 420

layout (location = 0) in vec2 vertex;
layout (location = 2) in vec2 uv;

out vec2 frag_uv;

void main() {
	gl_Position = vec4(vertex.x, vertex.y, 0.0, 1.0);
	frag_uv = uv;
}