#version 420
out vec4 FragColor;

in vec2 TexCoords;

layout (binding = 0) uniform sampler2D screen_texture;
layout (binding = 1) uniform sampler2D blur_texture;
uniform float bloomStrength = 0.04f;

vec3 exposure_tonemapping(vec3 color) {
    float exposure = 1;
    // tone mapping
    color = vec3(1.0) - exp(-color * exposure);
    return(color);
}

vec3 narkowicz_aces(vec3 color) {
    const float a = 2.51;
    const float b = 0.03;
    const float c = 2.43;
    const float d = 0.59;
    const float e = 0.14;
    return clamp((color * (a * color + b)) / (color * (c * color + d) + e), 0.0, 1.0);
}

void main() {
    vec3 hdrColor = texture(screen_texture, TexCoords).rgb;
    vec3 bloomColor = texture(blur_texture, TexCoords).rgb;
    
    bloomColor.x = clamp(bloomColor.x, 0.0, 4000.0);
    bloomColor.y = clamp(bloomColor.y, 0.0, 4000.0);
    bloomColor.z = clamp(bloomColor.z, 0.0, 4000.0);

    vec3 color = mix(hdrColor, bloomColor, bloomStrength); // linear interpolation

    const float gamma = 2.2;

    color = narkowicz_aces(color);
    // color = exposure_tonemapping(color);
    // also gamma correct while we're at it
    color = pow(color, vec3(1.0 / gamma));

    FragColor = vec4(color, 1.0);
}

