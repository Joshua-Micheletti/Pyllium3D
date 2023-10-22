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
    float focus_distance = 20;
    float focus_range = 50;

    float pi = 3.14159;

    vec4 focus_color = texture(screen_texture, frag_uv);
    vec4 blurred_color = texture(blurred_texture, frag_uv);
    vec4 depth = texture(depth_texture, frag_uv);

    depth.x = linearize_depth(depth.x, 0.1, 200.0);

    float blur = 0.0;

    if (depth.x >= focus_distance - focus_range && depth.x <= focus_distance + focus_range) {
        blur = (cos((depth.x - focus_distance) * (pi * (1/focus_range))) + 1) / 2;
    }

    frag_color = mix(blurred_color, focus_color, blur);
    // frag_color = vec4(blur, blur, blur, 1.0);
    // frag_color = vec4(depth.x, depth.x, depth.x, 1.0);
    // frag_color = blurred_color;
}