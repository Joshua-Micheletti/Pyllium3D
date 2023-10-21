#version 330

out vec4 frag_color;
  
in vec2 frag_uv;

uniform sampler2D screen_texture;

void main() {
    float tpi = 6.28318530718; // Pi*2
    
    // GAUSSIAN BLUR SETTINGS {{{
    float directions = 16.0; // BLUR DIRECTIONS (Default 16.0 - More is better but slower)
    float quality = 3.0; // BLUR QUALITY (Default 4.0 - More is better but slower)
    float size = 8.0; // BLUR SIZE (Radius)
    // GAUSSIAN BLUR SETTINGS }}}
   
    ivec2 resolution = textureSize(screen_texture, 0);

    vec2 radius = size / resolution.xy;
    
    // Normalized pixel coordinates (from 0 to 1)
    // vec2 uv = fragCoord/resolution.xy;
    // Pixel colour
    vec4 color = texture(screen_texture, frag_uv);
    
    // Blur calculations
    for (float d = 0.0; d < tpi; d += tpi / directions) {
		for(float i = 1.0 / quality; i <= 1.0; i += 1.0 / quality) {
			color += texture(screen_texture, frag_uv + vec2(cos(d), sin(d)) * radius * i);		
        }
    }
    
    // Output to screen
    color /= quality * directions - 15.0;
    frag_color = vec4(color.xyz, 1.0);
    
    // frag_color = vec4(col, 1.0);
    // vec2 tex_res = textureSize(screen_texture, 0);
    // float xs = tex_res.x;
    // float ys = tex_res.y;
    // float r = 5;

    // vec2 pos = frag_uv;
    // float x,y,xx,yy,rr=r*r,dx,dy,w,w0;
    // w0=0.3780/pow(r,1.975);
    // vec2 p;
    // vec4 col=vec4(0.0,0.0,0.0,0.0);
    // for (dx=1.0/xs,x=-r,p.x=0.5+(pos.x*0.5)+(x*dx);x<=r;x++,p.x+=dx){ xx=x*x;
    //  for (dy=1.0/ys,y=-r,p.y=0.5+(pos.y*0.5)+(y*dy);y<=r;y++,p.y+=dy){ yy=y*y;
    //   if (xx+yy<=rr)
    //     {
    //     w=w0*exp((-xx-yy)/(2.0*rr));
    //     col+=texture2D(screen_texture,p)*w;
    //     }}}
    // frag_color=col;
}  