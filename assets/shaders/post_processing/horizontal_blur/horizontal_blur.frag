#version 420

layout (binding = 0) uniform sampler2D screen_texture;

uniform float offset[3] = float[](0.0, 1.3846153846, 3.2307692308);
uniform float weight[3] = float[](0.2270270270, 0.3162162162, 0.0702702703);

out vec4 frag_color;

void main() {
    vec2 texture_size = textureSize(screen_texture, 0);
    frag_color = texture(screen_texture, vec2(gl_FragCoord) / texture_size) * weight[0];

    for (int i = 1; i < 3; i++) {
        frag_color += texture(screen_texture, (vec2(gl_FragCoord) + vec2(offset[i], 0.0)) / texture_size) * weight[i];
        frag_color += texture(screen_texture, (vec2(gl_FragCoord) - vec2(offset[i], 0.0)) / texture_size) * weight[i];
    }
}