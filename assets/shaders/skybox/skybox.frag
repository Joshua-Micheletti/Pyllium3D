#version 420 core
out vec4 FragColor;

in vec3 TexCoords;

layout (binding = 0) uniform samplerCube skybox;

void main() {
    FragColor = texture(skybox, TexCoords);
    // FragColor = TexCoords
    // FragColor = textureLod(skybox, TexCoords, 2.0);
    // FragColor = vec4(TexCoords, 1.0);
    // FragColor = vec4(1.0);
}