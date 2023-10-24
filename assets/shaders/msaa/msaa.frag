#version 330 core

in vec2 frag_uv;
flat in int frag_samples;

uniform sampler2DMS screen_texture_ms;

out vec4 frag_color;

void main() {
    vec4 color = vec4(0);

    ivec2 tex_size = textureSize(screen_texture_ms);

    for (int i = 0; i < frag_samples; i++) {
        color += texelFetch(screen_texture_ms, ivec2(tex_size.x * frag_uv.x, tex_size.y * frag_uv.y), i);
    }

    color /= frag_samples;

    frag_color = color;
}