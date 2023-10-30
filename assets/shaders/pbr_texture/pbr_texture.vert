# version 330

layout(location = 0) in vec3 vertex;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec2 uv;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
// uniform vec3 lights[100];
uniform vec3 eye;

uniform vec3 albedo;
uniform float roughness;
uniform float metallic;

// uniform vec3 light_colors[100];
// uniform float light_strengths[100];

// uniform float lights_count;

out vec3 frag_position;
out vec3 frag_normal;
out vec2 frag_uv;
// out vec3 frag_lights[100];
out vec3 frag_eye;

out vec3 frag_albedo;
out float frag_roughness;
out float frag_metallic;

// out vec3 frag_light_colors[100];
// out float frag_light_strengths[100];

// out float frag_lights_count;

void main() {
    mat4 mvp = projection * view * model;
    gl_Position = mvp * vec4(vertex, 1.0);
    
    frag_position = vec3(model * vec4(vertex, 1.0));

    frag_normal = mat3(transpose(inverse(model))) * normal;

    frag_uv = uv;

    // frag_lights = lights;
    frag_eye = eye;

    frag_albedo = albedo;
    frag_roughness = roughness;
    frag_metallic = metallic;

    // frag_light_colors = light_colors;
    // frag_light_strengths = light_strengths;

    // frag_lights_count = lights_count;
}