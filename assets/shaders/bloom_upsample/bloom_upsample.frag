

#version 330 core

// This shader performs upsampling on a texture,
// as taken from Call Of Duty method, presented at ACM Siggraph 2014.

// Remember to add bilinear minification filter for this texture!
// Remember to use a floating-point texture format (for HDR)!
// Remember to use edge clamping for this texture!
uniform sampler2D screen_texture;

uniform float radius;

in vec2 frag_uv;

out vec4 frag_color;

void main() {
	// The filter kernel is applied with a radius, specified in texture
	// coordinates, so that the radius will vary across mip resolutions.
	float x = radius;
	float y = radius;

	// Take 9 samples around current texel:
	// a - b - c
	// d - e - f
	// g - h - i
	// === ('e' is the current texel) ===
	vec3 a = texture(screen_texture, vec2(frag_uv.x - x, frag_uv.y + y)).rgb;
	vec3 b = texture(screen_texture, vec2(frag_uv.x,     frag_uv.y + y)).rgb;
	vec3 c = texture(screen_texture, vec2(frag_uv.x + x, frag_uv.y + y)).rgb;

	vec3 d = texture(screen_texture, vec2(frag_uv.x - x, frag_uv.y)).rgb;
	vec3 e = texture(screen_texture, vec2(frag_uv.x,     frag_uv.y)).rgb;
	vec3 f = texture(screen_texture, vec2(frag_uv.x + x, frag_uv.y)).rgb;

	vec3 g = texture(screen_texture, vec2(frag_uv.x - x, frag_uv.y - y)).rgb;
	vec3 h = texture(screen_texture, vec2(frag_uv.x,     frag_uv.y - y)).rgb;
	vec3 i = texture(screen_texture, vec2(frag_uv.x + x, frag_uv.y - y)).rgb;

	// Apply weighted distribution, by using a 3x3 tent filter:
	//  1   | 1 2 1 |
	// -- * | 2 4 2 |
	// 16   | 1 2 1 |
	vec3 upsample = e*4.0;
	upsample += (b+d+f+h)*2.0;
	upsample += (a+c+g+i);
	upsample *= 1.0 / 16.0;

    frag_color = vec4(upsample, 1.0);
}

