

#version 420
out vec4 FragColor;

in vec2 TexCoords;

layout (binding = 0) uniform sampler2D scene;
layout (binding = 1) uniform sampler2D bloomBlur;
uniform float bloomStrength = 0.4f;

vec3 bloom_none()
{
    vec3 hdrColor = texture(scene, TexCoords).rgb;
    return hdrColor;
}

vec3 bloom_old()
{
    vec3 hdrColor = texture(scene, TexCoords).rgb;
    vec3 bloomColor = texture(bloomBlur, TexCoords).rgb;
    return hdrColor + bloomColor; // additive blending
}

vec3 bloom_new() {
    vec3 hdrColor = texture(scene, TexCoords).rgb;
    vec3 bloomColor = texture(bloomBlur, TexCoords).rgb;
    return mix(hdrColor, bloomColor, bloomStrength); // linear interpolation
}

void main()
{
    // to bloom or not to bloom
    vec3 result = vec3(0.0);
    result = bloom_new();

    float exposure = 0.01;
    // tone mapping
    result = vec3(1.0) - exp(-result * exposure);
    // also gamma correct while we're at it
    const float gamma = 2.2;
    result = pow(result, vec3(1.0 / gamma));
    FragColor = vec4(result, 1.0);
}

