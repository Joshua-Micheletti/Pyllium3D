#version 330 core

in vec4 FragPos;

uniform vec3 light;
uniform float far_plane;

void main() {
    // get distance between fragment and light source
    float lightDistance = length(FragPos.xyz - light);
    
    // map to [0;1] range by dividing by far_plane
    lightDistance = lightDistance / far_plane;
    
    // write this as modified depth
    gl_FragDepth = lightDistance;
}  