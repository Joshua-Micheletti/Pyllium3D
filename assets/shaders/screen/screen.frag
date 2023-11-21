#version 330 core

out vec4 frag_color;
  
in vec2 frag_uv;

uniform sampler2D screen_texture;

void main() {
    frag_color = vec4(texture(screen_texture, frag_uv).rgb, 1.0);
    // frag_color = vec4(1.0, 0.5, 0.0, 1.0);
}