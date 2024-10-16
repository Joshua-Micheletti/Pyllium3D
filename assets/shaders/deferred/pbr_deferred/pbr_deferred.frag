#version 420 core

// in vec3 frag_position;
// in vec3 frag_normal;
in vec2 frag_uv;

uniform vec3 lights[100];
uniform vec3 eye;

// uniform vec3 albedo;
// uniform float roughness;
// uniform float metallic;

uniform vec3 light_colors[100];
uniform float light_strengths[100];
uniform float lights_count;

uniform float far_plane;
uniform vec3 light;

layout (binding = 0) uniform sampler2D position;
layout (binding = 1) uniform sampler2D normal;
layout (binding = 2) uniform sampler2D albedo_spec;
layout (binding = 7) uniform sampler2D pbr;
layout (binding = 3) uniform samplerCube depth_map;
layout (binding = 4) uniform samplerCube irradiance_map;
layout (binding = 5) uniform samplerCube reflection_map;
layout (binding = 6) uniform sampler2D brdf_integration;

out vec4 frag_color;

const float e = 2.71828;
const float PI = 3.14159265359;


float map(float value, float min1, float max1, float min2, float max2) {
    return min2 + (value - min1) * (max2 - min2) / (max1 - min1);
}

vec3 fresnel_schlick(float cosTheta, vec3 F0) {
    return F0 + (1.0 - F0) * pow(clamp(1.0 - cosTheta, 0.0, 1.0), 5.0);
}

vec3 fresnel_schlick_roughness(float cosTheta, vec3 F0, float roughness) {
    return F0 + (max(vec3(1.0 - roughness), F0) - F0) * pow(clamp(1.0 - cosTheta, 0.0, 1.0), 5.0);
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

    if (current_depth > far_plane) {
        return(1.0);
    }

    if (dot(frag_norm, frag_to_light) > 0) {
        return(1.0);
    }

    vec3 sample_offset[20] = vec3[](
        vec3( 1,  1,  1), vec3( 1, -1,  1), vec3(-1, -1,  1), vec3(-1,  1,  1), 
        vec3( 1,  1, -1), vec3( 1, -1, -1), vec3(-1, -1, -1), vec3(-1,  1, -1),
        vec3( 1,  1,  0), vec3( 1, -1,  0), vec3(-1, -1,  0), vec3(-1,  1,  0),
        vec3( 1,  0,  1), vec3(-1,  0,  1), vec3( 1,  0, -1), vec3(-1,  0, -1),
        vec3( 0,  1,  1), vec3( 0, -1,  1), vec3( 0, -1, -1), vec3( 0,  1, -1)
    );

    vec3 light_dir = normalize(light - frag_pos);

    float shadow  = 0.0;
    float bias = max(0.5 * (1.0 - dot(frag_norm, light_dir)), 0.05);

    int samples = 5;
    float disk_radius = 0.01;

    for (int i = 0; i < samples; i++) {
        float closest_depth = texture(depth_map, frag_to_light + sample_offset[i] * disk_radius).r;
        closest_depth *= far_plane;
        if (current_depth - bias > closest_depth) {
            shadow += 1.0;
        }
    }

    shadow /= float(samples);

    if (current_depth > far_plane / 2) {
        shadow += mix(0.0, 1.0, map(current_depth, far_plane / 2, far_plane / 1.2, 0.0, 1.0));
    }

    return(min(shadow, 1.0));
}

void main() {
    float ambient_occlusion = 1.0;

    vec3 frag_position = texture(position, frag_uv).rgb;
    vec3 frag_normal = texture(normal, frag_uv).rgb;
    vec3 albedo = texture(albedo_spec, frag_uv).rgb;
    vec2 material = texture(pbr, frag_uv).rg;
    float metallic = material.r;
    float roughness = material.g;

    vec3 normal = normalize(frag_normal);
    vec3 view_dir = normalize(eye - frag_position);
    vec3 reflection = reflect(-view_dir, normal);

    vec3 base_reflectivity = vec3(0.04); 
    base_reflectivity = mix(base_reflectivity, albedo, metallic);

    float shadow = (1.0 - shadow_calculation(frag_position, frag_normal));
    // reflectance equation
    vec3 light_output = vec3(0.0);

    vec3 F = fresnel_schlick_roughness(max(dot(normal, view_dir), 0.0), base_reflectivity, roughness);

    vec3 specular_energy = F;
    vec3 diffuse_energy = 1.0 - specular_energy;
    diffuse_energy *= 1.0 - metallic;

    vec3 irradiance = texture(irradiance_map, normal).rgb;
    vec3 diffuse = irradiance * albedo;

    const float MAX_REFLECTION_LOD = 4.0;
    vec3 prefiltered_color = textureLod(reflection_map, reflection, roughness * MAX_REFLECTION_LOD).rgb;
    vec2 brdf = texture(brdf_integration, vec2(max(dot(normal, view_dir), 0.0), roughness)).rg;
    vec3 specular = prefiltered_color * (F * brdf.x + brdf.y);

    vec3 ambient = (diffuse_energy * diffuse + specular) * ambient_occlusion;

    for (int i = 0; i < lights_count; i++) {
        // calculate per-light radiance
        vec3 light_direction = normalize(lights[i] - frag_position);
        vec3 halfway = normalize(view_dir + light_direction);
        float distance    = length(lights[i] - frag_position) / light_strengths[i];
        float attenuation = 1.0 / (distance * distance);
        vec3 radiance     = light_colors[i] * attenuation;        
        
        // cook-torrance brdf
        float NDF = DistributionGGX(normal, halfway, roughness);        
        float G   = GeometrySmith(normal, view_dir, light_direction, roughness);      
        vec3 F    = fresnel_schlick(max(dot(halfway, view_dir), 0.0), base_reflectivity);       
        
        vec3 kS = F;
        vec3 kD = vec3(1.0) - kS;
        kD *= 1.0 - metallic;	  
        
        vec3 numerator    = NDF * G * F;
        float denominator = 1.0 * max(dot(normal, view_dir), 0.0) * max(dot(normal, light_direction), 0.0) + 0.0001;
        vec3 specular     = numerator / denominator;  
            
        // add to outgoing radiance Lo
        float NdotL = max(dot(normal, light_direction), 0.0);                
        light_output += (kD * albedo / PI + specular) * radiance * NdotL;

        if (i == 0) {
            light_output = mix(vec3(0.0), light_output, shadow);;
        }
    }

    vec3 color = ambient + light_output;
	
    // color = color / (color + vec3(1.0));
    // color = pow(color, vec3(1.0/2.2));  
   
    frag_color = vec4(color, 1.0);
    // frag_color = vec4(0.5, 0.5, 0.5, 1.0);
    // frag_color = vec4(frag_uv.x, frag_uv.y, 0.0, 1.0);
}
