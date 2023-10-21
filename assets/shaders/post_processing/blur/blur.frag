#version 330

out vec4 frag_color;
  
in vec2 frag_uv;

uniform sampler2D screen_texture;

void main() {
    // const float offset = 1.0 / 300.0;
    vec2 tex_size = textureSize(screen_texture, 0);
    float offset_x = 1.0 / tex_size.x;
    float offset_y = 1.0 / tex_size.y;

    vec2 offsets[9] = vec2[](
        vec2(-offset_x,  offset_y), // top-left
        vec2( 0.0f,      offset_y), // top-center
        vec2( offset_x,  offset_y), // top-right
        vec2(-offset_x,  0.0f),   // center-left
        vec2( 0.0f,      0.0f),   // center-center
        vec2( offset_x,  0.0f),   // center-right
        vec2(-offset_x, -offset_y), // bottom-left
        vec2( 0.0f,     -offset_y), // bottom-center
        vec2( offset_x, -offset_y)  // bottom-right    
    );

    float kernel[9] = float[](
        1.0 / 16, 2.0 / 16, 1.0 / 16,
        2.0 / 16, 4.0 / 16, 2.0 / 16,
        1.0 / 16, 2.0 / 16, 1.0 / 16  
    );
    
    vec3 sample_tex[9];

    for(int i = 0; i < 9; i++) {
        sample_tex[i] = vec3(texture(screen_texture, frag_uv.st + offsets[i]));
    }

    vec3 col = vec3(0.0);

    for(int i = 0; i < 9; i++) {
        col += sample_tex[i] * kernel[i];
    }
    
    frag_color = vec4(col, 1.0);
}  