#version 420
out vec4 FragColor;

in vec2 TexCoords;

layout (binding = 0) uniform sampler2D screen_texture;
layout (binding = 1) uniform sampler2D blur_texture;
uniform float bloomStrength = 0.02f;

void main() {
    vec3 hdrColor = texture(screen_texture, TexCoords).rgb;
    vec3 bloomColor = texture(blur_texture, TexCoords).rgb;
    vec3 color = mix(hdrColor, bloomColor, bloomStrength); // linear interpolation

    // float exposure = 1;
    // // tone mapping
    // color = vec3(1.0) - exp(-color * exposure);
    // // also gamma correct while we're at it
    // const float gamma = 2.2;
    // color = pow(color, vec3(1.0 / gamma));
    FragColor = vec4(color, 1.0);
}

