#version 330 core
out vec4 frag_color;
in vec3 frag_position;

uniform sampler2D equirect_map;

const vec2 invAtan = vec2(0.1591, 0.3183);

vec2 sample_spherical_map(vec3 v) {
    vec2 uv = vec2(atan(v.z, v.x), asin(v.y));
    uv *= invAtan;
    uv += 0.5;
    return uv;
}

void main() {		
    vec2 uv = sample_spherical_map(normalize(frag_position)); // make sure to normalize localPos
    vec3 color = texture(equirect_map, uv).rgb;
    
    frag_color = vec4(color, 1.0);

    // frag_color = vec4(1.0, 0.5, 0.0, 1.0);
}