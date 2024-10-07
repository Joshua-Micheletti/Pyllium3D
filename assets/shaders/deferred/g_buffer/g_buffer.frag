#version 330 core
layout (location = 0) out vec3 g_position;
layout (location = 1) out vec3 g_normal;
layout (location = 2) out vec4 g_albedo_spec;
layout (location = 3) out vec2 g_pbr;

in vec3 frag_position;
in vec3 frag_normal;
in vec2 frag_uv;

// uniform sampler2D texture_diffuse1;
// uniform sampler2D texture_specular1;
uniform vec3 albedo;
uniform float metallic;
uniform float roughness;

void main()
{    
    // store the fragment position vector in the first gbuffer texture
    g_position = frag_position;
    // also store the per-fragment normals into the gbuffer
    g_normal = normalize(frag_normal);
    // and the diffuse per-fragment color
    g_albedo_spec.rgb = albedo;
    // store specular intensity in gAlbedoSpec's alpha component
    // gAlbedoSpec.a = texture(texture_specular1, TexCoords).r;
    g_pbr = vec2(metallic, roughness);
    
}  