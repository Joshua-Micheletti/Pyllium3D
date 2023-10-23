#version 330 core

in vec2 frag_uv;

uniform sampler2DMS screen_texture_ms;

out vec4 frag_color;

void main() {
    vec4 color = vec4(0);

    for (int i = 0; i < 8; i++) {
        color += texelFetch(screen_texture_ms, ivec2(frag_uv), i);
    }

    color /= 8;

    frag_color = color;
}