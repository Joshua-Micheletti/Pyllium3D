#version 330 core

out vec4 frag_color;
  
in vec2 frag_uv;

uniform sampler2D screen_texture;

void main() {
    frag_color = texture(screen_texture, frag_uv);
    float average = 0.2126 * frag_color.r + 0.7152 * frag_color.g + 0.0722 * frag_color.b;
    frag_color = vec4(average, average, average, 1.0);
}