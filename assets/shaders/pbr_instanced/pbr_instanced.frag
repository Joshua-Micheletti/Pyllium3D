#version 330 core

in vec3 frag_position;
in vec3 frag_normal;
in vec3 frag_light;
in vec3 frag_eye;

in vec3 frag_albedo;
in float frag_roughness;
in float frag_metallic;

in vec3 frag_light_color;

out vec4 frag_color;


const float PI = 3.14159265359;


vec3 fresnelSchlick(float cosTheta, vec3 F0)
{
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
    float ao = 1.0;
    float light_strength = 16.0;

    vec3 N = normalize(frag_normal);
    vec3 V = normalize(frag_eye - frag_position);

    vec3 F0 = vec3(0.04); 
    F0 = mix(F0, frag_albedo, frag_metallic);
	           
    // reflectance equation
    vec3 Lo = vec3(0.0);
    // calculate per-light radiance
    vec3 L = normalize(frag_light - frag_position);
    vec3 H = normalize(V + L);
    float distance    = length(frag_light - frag_position) / light_strength;
    float attenuation = 1.0 / (distance * distance);
    vec3 radiance     = frag_light_color * attenuation;        
    
    // cook-torrance brdf
    float NDF = DistributionGGX(N, H, frag_roughness);        
    float G   = GeometrySmith(N, V, L, frag_roughness);      
    vec3 F    = fresnelSchlick(max(dot(H, V), 0.0), F0);       
    
    vec3 kS = F;
    vec3 kD = vec3(1.0) - kS;
    kD *= 1.0 - frag_metallic;	  
    
    vec3 numerator    = NDF * G * F;
    float denominator = 1.0 * max(dot(N, V), 0.0) * max(dot(N, L), 0.0) + 0.0001;
    vec3 specular     = numerator / denominator;  
        
    // add to outgoing radiance Lo
    float NdotL = max(dot(N, L), 0.0);                
    Lo += (kD * frag_albedo / PI + specular) * radiance * NdotL; 

    vec3 ambient = vec3(0.03) * frag_albedo * ao;
    vec3 color = ambient + Lo;
	
    color = color / (color + vec3(1.0));
    color = pow(color, vec3(1.0/2.2));  
   
    frag_color = vec4(color, 1.0);
}