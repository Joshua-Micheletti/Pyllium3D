# version 330

layout(location = 0) in vec3 vertex;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec2 uv;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 light;
uniform vec3 eye;

out vec3 frag_position;
out vec3 frag_normal;
out vec3 frag_light;
out vec3 frag_eye;

void main() {
    gl_Position = projection * view * model * vec4(vertex, 1.0);
    
    frag_position = vec3(model * vec4(vertex, 1.0));
    frag_normal = vec3(normal.x, normal.y, normal.z);
    frag_light = light;
    frag_eye = eye;
}