#version 330 core

in vec3 frag_position;
in vec3 frag_normal;

in vec3 frag_albedo;
in float frag_roughness;
in float frag_metallic;


uniform vec3 eye;

uniform vec3 lights[100];
uniform vec3 light_colors[100];
uniform float light_strengths[100];
uniform float lights_count;

uniform float far_plane;
uniform samplerCube depth_map;
uniform vec3 light;

uniform samplerCube irradiance_map;

out vec4 frag_color;


const float PI = 3.14159265359;


vec3 fresnel_schlick(float cosTheta, vec3 F0) {
    return F0 + (1.0 - F0) * pow(clamp(1.0 - cosTheta, 0.0, 1.0), 5.0);
}

float DistributionGGX(vec3 N, vec3 H, float roughness) {
    float a      = roughness*roughness;
    float a2     = a*a;
    float NdotH  = max(dot(N, H), 0.0);
    float NdotH2 = NdotH*NdotH;
	
    float num   = a2;
    float denom = (NdotH2 * (a2 - 1.0) + 1.0);
    denom = PI * denom * denom;
	
    return num / denom;
}

float GeometrySchlickGGX(float NdotV, float roughness) {
    float r = (roughness + 1.0);
    float k = (r*r) / 8.0;

    float num   = NdotV;
    float denom = NdotV * (1.0 - k) + k;
	
    return num / denom;
}

float GeometrySmith(vec3 N, vec3 V, vec3 L, float roughness) {
    float NdotV = max(dot(N, V), 0.0);
    float NdotL = max(dot(N, L), 0.0);
    float ggx2  = GeometrySchlickGGX(NdotV, roughness);
    float ggx1  = GeometrySchlickGGX(NdotL, roughness);
	
    return ggx1 * ggx2;
}

float shadow_calculation(vec3 frag_pos, vec3 frag_norm) {
    vec3 frag_to_light = frag_pos - light;

    float current_depth = length(frag_to_light);

    if (dot(frag_norm, frag_to_light) > 0) {
        return(1.0 - (current_depth / far_plane));
    }

    if (current_depth > far_plane) {
        return(0.0);
    }

    vec3 sample_offset[20] = vec3[](
        vec3( 1,  1,  1), vec3( 1, -1,  1), vec3(-1, -1,  1), vec3(-1,  1,  1), 
        vec3( 1,  1, -1), vec3( 1, -1, -1), vec3(-1, -1, -1), vec3(-1,  1, -1),
        vec3( 1,  1,  0), vec3( 1, -1,  0), vec3(-1, -1,  0), vec3(-1,  1,  0),
        vec3( 1,  0,  1), vec3(-1,  0,  1), vec3( 1,  0, -1), vec3(-1,  0, -1),
        vec3( 0,  1,  1), vec3( 0, -1,  1), vec3( 0, -1, -1), vec3( 0,  1, -1)
    );

    vec3 light_dir = normalize(light - frag_position);

    float shadow  = 0.0;
    float bias = max(0.5 * (1.0 - dot(frag_norm, light_dir)), 0.05);

    int samples = 20;
    float disk_radius = 0.005;

    for (int i = 0; i < samples; i++) {
        float closest_depth = texture(depth_map, frag_to_light + sample_offset[i] * disk_radius).r;
        closest_depth *= far_plane;
        if (current_depth - bias > closest_depth) {
            shadow += 1.0;
        }
    }

    shadow /= float(samples);
    shadow *= 1.0 - (current_depth / far_plane);

    return(shadow);
}

void main() {
    float ambient_occlusion = 1.0;

    vec3 normal = normalize(frag_normal);
    vec3 view_dir = normalize(eye - frag_position);

    vec3 base_reflectivity = vec3(0.04); 
    base_reflectivity = mix(base_reflectivity, frag_albedo, frag_metallic);
	           
    // reflectance equation
    vec3 light_output = vec3(0.0);

    for (int i = 0; i < lights_count; i++) {
        // calculate per-light radiance
        vec3 light_direction = normalize(lights[i] - frag_position);
        vec3 halfway = normalize(view_dir + light_direction);
        float distance = length(lights[i] - frag_position) / light_strengths[i];
        float attenuation = 1.0 / (distance * distance);
        vec3 radiance = light_colors[i] * attenuation;        
        
        // cook-torrance brdf
        float NDF = DistributionGGX(normal, halfway, frag_roughness);        
        float geometry = GeometrySmith(normal, view_dir, light_direction, frag_roughness);      
        vec3 fresnel = fresnel_schlick(max(dot(halfway, view_dir), 0.0), base_reflectivity);       
        
        vec3 kS = fresnel;
        vec3 kD = vec3(1.0) - kS;
        kD *= 1.0 - frag_metallic;	  
        
        vec3 numerator    = NDF * geometry * fresnel;
        float denominator = 1.0 * max(dot(normal, view_dir), 0.0) * max(dot(normal, light_direction), 0.0) + 0.0001;
        vec3 specular     = numerator / denominator;  
            
        // add to outgoing radiance Lo
        float NdotL = max(dot(normal, light_direction), 0.0);                
        light_output += (kD * frag_albedo / PI + specular) * radiance * NdotL;
    }

    

    // vec3 ambient = vec3(0.03) * base_reflectivity * ambient_occlusion;
    // vec3 color = ambient + light_output;
    vec3 kS = fresnel_schlick(max(dot(normal, view_dir), 0.0), base_reflectivity);
    vec3 kD = 1.0 - kS;

    kD *= 1.0 - frag_metallic;

    vec3 irradiance = texture(irradiance_map, normal).rgb;
    vec3 diffuse = irradiance * frag_albedo;
    vec3 ambient = (kD * diffuse) * ambient_occlusion;

    vec3 color = ambient + light_output;

    float shadow = shadow_calculation(frag_position, frag_normal);
    color *= (1.0 - shadow);
	
    color = color / (color + vec3(1.0));
    color = pow(color, vec3(1.0/2.2));  
   
    frag_color = vec4(color, 1.0);
    // frag_color = vec4(model_color, 1.0);
    // frag_color = vec4(vec3(shadow), 1.0);
}
