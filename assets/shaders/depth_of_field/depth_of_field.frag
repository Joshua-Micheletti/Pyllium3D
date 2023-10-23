#version 330 core

in vec2 frag_uv;

uniform sampler2D screen_texture;
uniform sampler2D blurred_texture;
uniform sampler2D depth_texture;

out vec4 frag_color;

float linearize_depth(float d, float zNear, float zFar) {
    return zNear * zFar / (zFar + d * (zNear - zFar));
}

void main() {
    float min_distance = 1.0;
    float max_distance = 30.0;

    vec4 focus_color = texture(screen_texture, frag_uv);
    vec4 blurred_color = texture(blurred_texture, frag_uv);
    vec4 depth = texture(depth_texture, frag_uv);
    vec4 focus_point = texture(depth_texture, vec2(0.5, 0.5));

    float dist = length(linearize_depth(depth.x, 0.1, 2000) - linearize_depth(focus_point.x, 0.1, 2000));
    // float linearized_dist = linearize_depth(dist, 0.1, 200);

    // float blur = smoothstep(min_distance, max_distance, length(depth.x - focus_point.x));
    float blur = smoothstep(min_distance, max_distance, dist);

    frag_color = mix(focus_color, blurred_color, blur);
    // frag_color = vec4(blur, blur, blur, 1.0);
    // float diff = abs(depth.x - focus_point.x);

    // frag_color = vec4(diff, diff, diff, 1.0);
    // frag_color = texture(depth_texture, frag_uv);
}