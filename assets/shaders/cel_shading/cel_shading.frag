# version 330

in vec3 frag_position;
in vec3 frag_normal;
in vec3 frag_light;
in vec3 frag_eye;

in vec3 frag_ambient;
in vec3 frag_diffuse;
in vec3 frag_specular;
in float frag_shininess;

in vec3 frag_light_ambient;
in vec3 frag_light_diffuse;
in vec3 frag_light_specular;

out vec4 frag_color;

void main() {
    float shininess = frag_shininess;

    // ambient
    vec3 ambient = frag_light_ambient * frag_ambient;

    // diffuse
    vec3 normal = normalize(frag_normal);
    vec3 light_dir = normalize(frag_light - frag_position);

    float diffuse_strength = max(dot(normal, light_dir), 0.0);
    // vec3 diffuse =  frag_light_diffuse * (diffuse_strength * frag_diffuse);

    // specular
    vec3 specular = vec3(0.0);

    vec3 view_dir = normalize(frag_eye - frag_position);

    // if (diffuse != vec3(0.0)) {
        
    //     // phong model
    //     // vec3 reflect_dir = reflect(-light_dir, normal);
    //     // blinn model
    vec3 halfway_dir = normalize(light_dir + view_dir);

    //     // phong model
    //     // float raw_specular = pow(max(dot(view_dir, reflect_dir), 0.0), shininess);
    //     // blinn model
    float raw_specular = pow(max(dot(normal, halfway_dir), 0.0), shininess);

    raw_specular *= dot(normal, light_dir);

    //     specular = frag_light_specular * (frag_specular * raw_specular);
    // }

    float light_intensity = 0.6 * diffuse_strength + 0.6 * raw_specular;

    vec3 color;

    if (dot(view_dir, normal) < 0.3) {
        color = vec3(0, 0, 0);
    } else {
        if (light_intensity > 0.9) {
            light_intensity = 1.1;
        } else if (light_intensity > 0.5) {
            light_intensity = 0.7;
        } else {
            light_intensity = 0.5;
        }
    }

    frag_color = vec4(light_intensity, light_intensity, light_intensity, 1.0);
}