#version 330

out vec4 frag_color;
  
in vec2 frag_uv;

uniform sampler2D screen_texture;

vec4 gaussian() {
    float Pi = 6.28318530718; // Pi*2
    
    // GAUSSIAN BLUR SETTINGS {{{
    float Directions = 8.0; // BLUR DIRECTIONS (Default 16.0 - More is better but slower)
    float Quality = 3.0; // BLUR QUALITY (Default 4.0 - More is better but slower)
    float Size = 4.0; // BLUR SIZE (Radius)
    // GAUSSIAN BLUR SETTINGS }}}

    ivec2 iResolution = textureSize(screen_texture, 0);
   
    vec2 Radius = Size/iResolution.xy;
    
    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = frag_uv;
    // Pixel colour
    vec4 Color = texture(screen_texture, uv);
    
    // Blur calculations
    for( float d=0.0; d<Pi; d+=Pi/Directions) {
		for(float i=1.0/Quality; i<=1.0; i+=1.0/Quality) {
			Color += texture( screen_texture, uv+vec2(cos(d),sin(d))*Radius*i);		
        }
    }
    
    // Output to screen
    Color /= Quality * Directions + 1.0;
    return(Color);
}

void main() {
    // const float offset = 1.0 / 300.0;
    // vec2 tex_size = textureSize(screen_texture, 0);
    // float offset_x = 1.0 / tex_size.x;
    // float offset_y = 1.0 / tex_size.y;

    // vec2 offsets[9] = vec2[](
    //     vec2(-offset_x,  offset_y), // top-left
    //     vec2( 0.0f,      offset_y), // top-center
    //     vec2( offset_x,  offset_y), // top-right
    //     vec2(-offset_x,  0.0f),   // center-left
    //     vec2( 0.0f,      0.0f),   // center-center
    //     vec2( offset_x,  0.0f),   // center-right
    //     vec2(-offset_x, -offset_y), // bottom-left
    //     vec2( 0.0f,     -offset_y), // bottom-center
    //     vec2( offset_x, -offset_y)  // bottom-right    
    // );

    // float kernel[9] = float[](
    //     1.0 / 16, 2.0 / 16, 1.0 / 16,
    //     2.0 / 16, 4.0 / 16, 2.0 / 16,
    //     1.0 / 16, 2.0 / 16, 1.0 / 16  
    // );
    
    // vec3 sample_tex[9];
    // vec3 col = vec3(0.0);

    // for(int i = 0; i < 9; i++) {
    //     sample_tex[i] = vec3(texture(screen_texture, frag_uv.st + offsets[i]));
    //     col += sample_tex[i] * kernel[i];
    // }
    
    // frag_color = vec4(col, 1.0);
    frag_color = gaussian();
}  