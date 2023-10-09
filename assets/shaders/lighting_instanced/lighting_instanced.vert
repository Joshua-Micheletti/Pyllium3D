# version 330

layout(location = 0) in vec3 vertex;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec2 uv;
layout(location = 3) in mat4 model;
layout(location = 7) in vec3 ambient;
layout(location = 8) in vec3 diffuse;
layout(location = 9) in vec3 specular;
layout(location = 10) in float shininess;

// uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 light;
uniform vec3 eye;

// uniform vec3 ambient;
// uniform vec3 diffuse;
// uniform vec3 specular;
// uniform float shininess;

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

// out float frag_instance;
out mat4 frag_model;

void main() {
    gl_Position = (projection * view * model * vec4(vertex, 1.0));
    
    frag_position = vec3(model * vec4(vertex, 1.0));
    frag_normal = vec3(normal.x, normal.y, normal.z);
    frag_light = light;
    frag_eye = eye;

    frag_ambient = ambient;
    frag_diffuse = diffuse;
    frag_specular = specular;
    frag_shininess = shininess;

    frag_light_ambient = light_ambient;
    frag_light_diffuse = light_diffuse;
    frag_light_specular = light_specular;

    // frag_instance = instance;
    frag_model = model;
}