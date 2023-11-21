#version 330 core

// This shader performs downsampling on a texture,
// as taken from Call Of Duty method, presented at ACM Siggraph 2014.
// This particular method was customly designed to eliminate
// "pulsating artifacts and temporal stability issues".

// Remember to add bilinear minification filter for this texture!
// Remember to use a floating-point texture format (for HDR)!
// Remember to use edge clamping for this texture!
uniform sampler2D screen_texture;
uniform vec2 src_resolution;

// which mip we are writing to, used for Karis average
uniform int mipLevel = 1;

in vec2 frag_uv;
out vec4 frag_color;

vec3 PowVec3(vec3 v, float p)
{
    return vec3(pow(v.x, p), pow(v.y, p), pow(v.z, p));
}

const float invGamma = 1.0 / 2.2;
vec3 ToSRGB(vec3 v)   { return PowVec3(v, invGamma); }

float sRGBToLuma(vec3 col)
{
    //return dot(col, vec3(0.2126f, 0.7152f, 0.0722f));
	return dot(col, vec3(0.299f, 0.587f, 0.114f));
}

float KarisAverage(vec3 col)
{
	// Formula is 1 / (1 + luma)
	float luma = sRGBToLuma(ToSRGB(col)) * 0.25f;
	return 1.0f / (1.0f + luma);
}

// NOTE: This is the readable version of this shader. It will be optimized!
void main()
{
	vec2 srcTexelSize = 1.0 / src_resolution;
	float x = srcTexelSize.x;
	float y = srcTexelSize.y;

	// Take 13 samples around current texel:
	// a - b - c
	// - j - k -
	// d - e - f
	// - l - m -
	// g - h - i
	// === ('e' is the current texel) ===
	vec3 a = texture(screen_texture, vec2(frag_uv.x - 2*x, frag_uv.y + 2*y)).rgb;
	vec3 b = texture(screen_texture, vec2(frag_uv.x,       frag_uv.y + 2*y)).rgb;
	vec3 c = texture(screen_texture, vec2(frag_uv.x + 2*x, frag_uv.y + 2*y)).rgb;

	vec3 d = texture(screen_texture, vec2(frag_uv.x - 2*x, frag_uv.y)).rgb;
	vec3 e = texture(screen_texture, vec2(frag_uv.x,       frag_uv.y)).rgb;
	vec3 f = texture(screen_texture, vec2(frag_uv.x + 2*x, frag_uv.y)).rgb;

	vec3 g = texture(screen_texture, vec2(frag_uv.x - 2*x, frag_uv.y - 2*y)).rgb;
	vec3 h = texture(screen_texture, vec2(frag_uv.x,       frag_uv.y - 2*y)).rgb;
	vec3 i = texture(screen_texture, vec2(frag_uv.x + 2*x, frag_uv.y - 2*y)).rgb;

	vec3 j = texture(screen_texture, vec2(frag_uv.x - x, frag_uv.y + y)).rgb;
	vec3 k = texture(screen_texture, vec2(frag_uv.x + x, frag_uv.y + y)).rgb;
	vec3 l = texture(screen_texture, vec2(frag_uv.x - x, frag_uv.y - y)).rgb;
	vec3 m = texture(screen_texture, vec2(frag_uv.x + x, frag_uv.y - y)).rgb;

	// Apply weighted distribution:
	// 0.5 + 0.125 + 0.125 + 0.125 + 0.125 = 1
	// a,b,d,e * 0.125
	// b,c,e,f * 0.125
	// d,e,g,h * 0.125
	// e,f,h,i * 0.125
	// j,k,l,m * 0.5
	// This shows 5 square areas that are being sampled. But some of them overlap,
	// so to have an energy preserving downsample we need to make some adjustments.
	// The weights are the distributed, so that the sum of j,k,l,m (e.g.)
	// contribute 0.5 to the final color output. The code below is written
	// to effectively yield this sum. We get:
	// 0.125*5 + 0.03125*4 + 0.0625*4 = 1

    vec3 downsample = vec3(0.0);

	// Check if we need to perform Karis average on each block of 4 samples
	vec3 groups[5];
	switch (mipLevel)
	{
	case 0:
	  // We are writing to mip 0, so we need to apply Karis average to each block
	  // of 4 samples to prevent fireflies (very bright subpixels, leads to pulsating
	  // artifacts).
	  groups[0] = (a+b+d+e) * (0.125f/4.0f);
	  groups[1] = (b+c+e+f) * (0.125f/4.0f);
	  groups[2] = (d+e+g+h) * (0.125f/4.0f);
	  groups[3] = (e+f+h+i) * (0.125f/4.0f);
	  groups[4] = (j+k+l+m) * (0.5f/4.0f);
	  groups[0] *= KarisAverage(groups[0]);
	  groups[1] *= KarisAverage(groups[1]);
	  groups[2] *= KarisAverage(groups[2]);
	  groups[3] *= KarisAverage(groups[3]);
	  groups[4] *= KarisAverage(groups[4]);
	  downsample = groups[0]+groups[1]+groups[2]+groups[3]+groups[4];
	  downsample = max(downsample, 0.0001f);
	  break;
	default:
	  downsample = e*0.125;                // ok
	  downsample += (a+c+g+i)*0.03125;     // ok
	  downsample += (b+d+f+h)*0.0625;      // ok
	  downsample += (j+k+l+m)*0.125;       // ok
	  break;
	}

    frag_color = vec4(downsample, 1.0);
}

