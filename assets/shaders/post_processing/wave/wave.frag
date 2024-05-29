#version 330 core

in vec2 frag_uv;
in float frag_time;

uniform sampler2D screen_texture;

out vec4 frag_color;

void main() {
    vec2 tex_coords = vec2(frag_uv.x + sin(frag_uv.y * 4 * 2 * 3.14159 + frag_time) / 100, frag_uv.y);
    // frag_uv.x += sin(frag_uv.y * 4*2*3.14159 + frag_time) / 100;
    frag_color = texture(screen_texture, tex_coords);
}