#version 330 core

out vec4 frag_color;
  
in vec2 frag_uv;

uniform sampler2D screen_texture;

float linearize_depth(in vec2 uv) {
    float z_near = 0.5;
    float z_far = 100.0;
    float depth = texture2D(screen_texture, uv).x;
    return((2.0 * z_near) / (z_far + z_near - depth * (z_far - z_near)));
}

void main() {
    float c = linearize_depth(frag_uv);
    frag_color = vec4(c, c, c, 1.0);
}