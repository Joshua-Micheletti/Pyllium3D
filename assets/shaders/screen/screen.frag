#version 330 core

out vec4 frag_color;
  
in vec2 frag_uv;

uniform sampler2D screen_texture;

void main() {
    frag_color = texture(screen_texture, frag_uv);
}