# version 330

layout(location = 0) in vec3 vertex;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec2 uv;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 light;
uniform vec3 eye;

uniform vec3 ambient;
uniform vec3 diffuse;
uniform vec3 specular;
uniform float shininess;

uniform vec3 light_ambient;
uniform vec3 light_diffuse;
uniform vec3 light_specular;

out vec3 frag_position;
out vec3 frag_normal;
out vec3 frag_light;
out vec3 frag_eye;

out vec3 frag_ambient;
out vec3 frag_diffuse;
out vec3 frag_specular;
out float frag_shininess;

out vec3 frag_light_ambient;
out vec3 frag_light_diffuse;
out vec3 frag_light_specular;

void main() {
    mat4 mvp = projection * view * model;
    gl_Position = mvp * vec4(vertex, 1.0);
    
    frag_position = vec3(model * vec4(vertex, 1.0));

    frag_normal = mat3(transpose(inverse(model))) * normal;

    frag_light = light;
    frag_eye = eye;

    frag_ambient = ambient;
    frag_diffuse = diffuse;
    frag_specular = specular;
    frag_shininess = shininess;

    frag_light_ambient = light_ambient;
    frag_light_diffuse = light_diffuse;
    frag_light_specular = light_specular;
}