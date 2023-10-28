# version 330

layout(location = 0) in vec3 vertex;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec2 uv;
layout(location = 3) in mat4 model;
layout(location = 8) in vec3 albedo;
layout(location = 11) in float roughness;
layout(location = 12) in float metallic;

uniform mat4 view;
uniform mat4 projection;
uniform vec3 eye;

uniform vec3 light_color;
uniform float light_strength;

out vec3 frag_position;
out vec3 frag_normal;
out vec3 frag_eye;

out vec3 frag_albedo;
out float frag_roughness;
out float frag_metallic;

void main() {
    mat4 mvp = projection * view * model;
    gl_Position = mvp * vec4(vertex, 1.0);
    
    frag_position = vec3(model * vec4(vertex, 1.0));

    frag_normal = mat3(transpose(inverse(model))) * normal;

    frag_eye = eye;

    frag_albedo = albedo;
    frag_roughness = roughness;
    frag_metallic = metallic;
}