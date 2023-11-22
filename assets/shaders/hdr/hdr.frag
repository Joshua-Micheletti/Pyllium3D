#version 420

in vec2 frag_uv;

layout (binding = 0) uniform sampler2D screen_texture;

out vec4 frag_color;

void main() {
    float exposure = 1;
    const float gamma = 2.2;

    vec3 color = texture(screen_texture, frag_uv).rgb;
    // tone mapping
    color = vec3(1.0) - exp(-color * exposure);
    // also gamma correct while we're at it
    color = pow(color, vec3(1.0 / gamma));
    frag_color = vec4(color, 1.0);
}