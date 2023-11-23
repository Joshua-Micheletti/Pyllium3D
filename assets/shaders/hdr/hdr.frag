#version 420

in vec2 frag_uv;

layout (binding = 0) uniform sampler2D screen_texture;

out vec4 frag_color;

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
    
    const float gamma = 2.2;
    vec3 color = texture(screen_texture, frag_uv).rgb;
    
    // color = exposure_tonemapping(color);
    color = narkowicz_aces(color);
    // also gamma correct while we're at it
    color = pow(color, vec3(1.0 / gamma));
    frag_color = vec4(color, 1.0);
}