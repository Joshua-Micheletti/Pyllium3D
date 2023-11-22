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

in mat4 frag_model;

out vec4 frag_color;

void main() {
    float shininess = frag_shininess;

    // ambient
    vec3 ambient = frag_light_ambient * frag_ambient;

    // diffuse
    vec3 normal = normalize(frag_normal);
    vec3 light_dir = normalize(frag_light - frag_position);

    float diffuse_strength = max(dot(normal, light_dir), 0.0);
    vec3 diffuse =  frag_light_diffuse * (diffuse_strength * frag_diffuse);

    // specular
    vec3 specular = vec3(0.0);

    

    if (diffuse != vec3(0.0)) {
        vec3 view_dir = normalize(frag_eye - frag_position);
        // phong model
        // vec3 reflect_dir = reflect(-light_dir, normal);
        // blinn model
        vec3 halfway_dir = normalize(light_dir + view_dir);

        // phong model
        // float raw_specular = pow(max(dot(view_dir, reflect_dir), 0.0), shininess);
        // blinn model
        float raw_specular = pow(max(dot(normal, halfway_dir), 0.0), shininess);

        raw_specular *= dot(normal, light_dir);

        specular = frag_light_specular * (frag_specular * raw_specular);
    }

    vec3 color = (ambient + diffuse + specular);

    frag_color = vec4(color, 1.0);   
}