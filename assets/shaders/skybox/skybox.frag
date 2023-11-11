#version 330 core
out vec4 FragColor;

in vec3 TexCoords;

uniform samplerCube skybox;

void main() {
    FragColor = texture(skybox, TexCoords);
    // FragColor = textureLod(skybox, TexCoords, 2.0);
    // FragColor = vec4(TexCoords, 1.0);
}