#version 330 core

in vec3 frag_position;
in vec3 frag_normal;
in vec3 frag_light;
in vec3 frag_eye;

in vec3 frag_albedo;
in float frag_roughness;
in float frag_metallic;

in vec3 frag_light_color;
in float frag_light_strength;

out vec4 frag_color;


const float PI = 3.14159265359;


vec3 fresnel_schlick(float cosTheta, vec3 F0) {
    return F0 + (1.0 - F0) * pow(clamp(1.0 - cosTheta, 0.0, 1.0), 5.0);
}

float DistributionGGX(vec3 N, vec3 H, float roughness)
{
    float a      = roughness*roughness;
    float a2     = a*a;
    float NdotH  = max(dot(N, H), 0.0);
    float NdotH2 = NdotH*NdotH;
	
    float num   = a2;
    float denom = (NdotH2 * (a2 - 1.0) + 1.0);
    denom = PI * denom * denom;
	
    return num / denom;
}

float GeometrySchlickGGX(float NdotV, float roughness)
{
    float r = (roughness + 1.0);
    float k = (r*r) / 8.0;

    float num   = NdotV;
    float denom = NdotV * (1.0 - k) + k;
	
    return num / denom;
}
float GeometrySmith(vec3 N, vec3 V, vec3 L, float roughness)
{
    float NdotV = max(dot(N, V), 0.0);
    float NdotL = max(dot(N, L), 0.0);
    float ggx2  = GeometrySchlickGGX(NdotV, roughness);
    float ggx1  = GeometrySchlickGGX(NdotL, roughness);
	
    return ggx1 * ggx2;
}

void main() {
    float ambient_occlusion = 1.0;
    float light_strength = frag_light_strength;

    vec3 normal = normalize(frag_normal);
    vec3 view_dir = normalize(frag_eye - frag_position);

    vec3 model_color = vec3(0.04); 
    model_color = mix(model_color, frag_albedo, frag_metallic);
	           
    // reflectance equation
    vec3 light_output = vec3(0.0);
    // calculate per-light radiance
    vec3 light_direction = normalize(frag_light - frag_position);
    vec3 halfway = normalize(view_dir + light_direction);
    float distance = length(frag_light - frag_position) / light_strength;
    float attenuation = 1.0 / (distance * distance);
    vec3 radiance = frag_light_color * attenuation;        
    
    // cook-torrance brdf
    float NDF = DistributionGGX(normal, halfway, frag_roughness);        
    float geometry = GeometrySmith(normal, view_dir, light_direction, frag_roughness);      
    vec3 fresnel = fresnel_schlick(max(dot(halfway, view_dir), 0.0), model_color);       
    
    vec3 kS = fresnel;
    vec3 kD = vec3(1.0) - kS;
    kD *= 1.0 - frag_metallic;	  
    
    vec3 numerator    = NDF * geometry * fresnel;
    float denominator = 1.0 * max(dot(normal, view_dir), 0.0) * max(dot(normal, light_direction), 0.0) + 0.0001;
    vec3 specular     = numerator / denominator;  
        
    // add to outgoing radiance Lo
    float NdotL = max(dot(normal, light_direction), 0.0);                
    light_output += (kD * frag_albedo / PI + specular) * radiance * NdotL; 

    vec3 ambient = vec3(0.03) * frag_albedo * ambient_occlusion;
    vec3 color = ambient + light_output;
	
    color = color / (color + vec3(1.0));
    color = pow(color, vec3(1.0/2.2));  
   
    frag_color = vec4(color, 1.0);
}
