#version 420

in vec2 frag_uv;

layout (binding = 0) uniform sampler2D screen_texture;
// uniform float[10] gaussian_kernel;

uniform float offset[5] = float[](0.0, 1.0, 2.0, 3.0, 4.0);
uniform float weight[5] = float[](0.2270270270, 0.1945945946, 0.1216216216,
                                  0.0540540541, 0.0162162162);

out vec4 frag_color;

void main() {
    vec2 texture_size = textureSize(screen_texture, 0);
    // vec2 texelSize = 1. / textureSize(screen_texture, 0);
    vec2 screen_uv = frag_uv * texture_size;



    // // float radius = 0.5;
    
    // // float sigma = mix(.1, 32., radius);
    // // int kernel_size = 2 * int(floor(4. * sigma + .5)) + 1;
    // // float[10] gaussian_kernel = float[10](0.01289634, 0.06175875, 0.20881797, 0.49851087, 0.8402696, 1.0, 0.8402696, 0.49851087, 0.20881797, 0.06175875);

    // float sigma = 1.695;
    // int kernel_size = 10;
    
    // float weightSum = 0.;
    // frag_color = vec4(0.);

    // for (int i = 0; i < kernel_size; i++) {
    //     float x = float(i) - (float(kernel_size) * .5);
    //     // float weight = exp(-(x * x) / (2.0 * sigma * sigma));
    //     // weightSum += weight;
    //     weightSum += gaussian_kernel[i];
        
    //     frag_color += texture(screen_texture, frag_uv + vec2(0., x * texelSize.y)) * gaussian_kernel[i];
    // }

    // frag_color /= weightSum;
    
    // frag_color = vec4(frag_color.rgb, 1.0);

    frag_color = texture2D(screen_texture, vec2(gl_FragCoord) / texture_size) * weight[0];

    for (int i=1; i<5; i++) {
        frag_color += texture2D(screen_texture, (vec2(gl_FragCoord) + vec2(0.0, offset[i])) / texture_size.y) * weight[i];
        frag_color += texture2D(screen_texture, (vec2(gl_FragCoord) - vec2(0.0, offset[i])) / texture_size.y) * weight[i];
    }

    // frag_color = vec4(screen_uv / texture_size, 0.0, 1.0);
    // frag_color = vec4(gl_FragCoord.xy / texture_size, 0.0, 1.0);
}