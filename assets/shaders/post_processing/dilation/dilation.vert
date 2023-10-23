#version 330 core
layout (location = 0) in vec2 vertex;
layout (location = 2) in vec2 uv;

// uniform float user_parameter_0;
// uniform float user_parameter_1;

out vec2 frag_uv;
// out float frag_param_0;
// out float frag_param_1; 

void main() {
    gl_Position = vec4(vertex.x, vertex.y, 0.0, 1.0); 
    frag_uv = uv;

    // frag_param_0 = user_parameter_0;
    // frag_param_1 = user_parameter_1;
}  