#version 330 core

out vec4 frag_color;
  
in vec2 frag_uv;

uniform sampler2D screen_texture;

void main() {
    frag_color = vec4(vec3(1.0 - texture(screen_texture, frag_uv)), 1.0);
}