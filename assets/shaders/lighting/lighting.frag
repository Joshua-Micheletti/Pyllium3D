# version 330

in vec3 frag_position;
in vec3 frag_normal;
in vec3 frag_light;
in vec3 frag_eye;

out vec4 frag_color;

void main() {
    float ambient_strength = 0.3;
    float specular_strength = 0.5;
    float shininess = 32;

    vec3 light_color = vec3(1.0);
    vec3 object_color = vec3(0.2, 0.3, 1.0);

    vec3 ambient = ambient_strength * light_color;

    vec3 normal = normalize(frag_normal);
    vec3 light_dir = normalize(frag_light - frag_position);

    float diffuse_strength = max(dot(normal, light_dir), 0.0);
    vec3 diffuse = diffuse_strength * light_color;

    vec3 view_dir = normalize(frag_eye - frag_position);
    vec3 reflect_dir = reflect(-light_dir, normal);

    float raw_specular = pow(max(dot(view_dir, reflect_dir), 0.0), shininess);
    vec3 specular = specular_strength * raw_specular * light_color;

    vec3 color = (ambient + diffuse + specular) * object_color;

    frag_color = vec4(color, 1.0);
}