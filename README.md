# Pyllium3D
## Description
A 3D engine using the OpenGL API for graphics and Bullet API for physics

## Requirements
Python 3  
OpenGL 4.5

## Installation
- `git clone https://github.com/Joshua-Micheletti/Pyllium3D`
  - (Alternative) Download the repository and extract it
- `cd Pyllium3D`
- `pip install -r requirements.txt`

### Execution
`python src/main.py`

## Usage
### Creating the scene
To create a scene in the engine, head over to the `src/scene.py` file and delete all the content of the `setup()` and `update()` functions.  
All the code that will be written inside the `setup()` function will execute once at startup, while the code contained inside the `update()` function will execute every cycle.

### RendererManager
All the rendering functionality required to display images is contained in the `RendererManager` object:
- Import the class with the import: `from renderer/renderer_manager import RendererManager`
- create a reference to the RendererManager object for quick access: `rm = RendererManager()`

The renderer manager is a singleton, so you will always obtain the same object by calling `RendererManager()`, and it won't be lost even if its reference inside `scene.py` is lost.

This object allows the user to:
- load meshes
- load textures
- load shaders
- create materials
- create models
- create lights
- create instances
- modify all the above

### Loading a mesh
Meshes are the 3D vertex data that represents a 3D object.  
For now the program only supports Wavefront OBJ meshes.  
To speed up loading times, it's also possible to load JSON indiced 3D meshes (created with [ModelIndexer](https://github.com/Joshua-Micheletti/ModelIndexer))  

Every mesh is identified with a unique name, so to create a new mesh, there are 2 options:
- `rm.new_mesh(name, path_to_obj_file)`
- `rm.new_json_mesh(name, path_to_json_file)`

Both arguments are of type string.

When it comes to load times, `rm.new_mesh` is several times slower than precomputing a JSON and loading it with `rm.new_json_mesh`, so when possible, it's better to load a mesh through an indiced JSON.  
Both functions will print a message in blue showing the time it was printed, the name of the mesh and the time it took to load it.

As an example, here we can see the loading time difference of a 3D mesh with 804 indiced triangles:
- `new_json_mesh()`: [1.39] Created mesh: gally in 0.01s
- `new_mesh()`: [2.52] Created mesh: gally in 1.14s

Remember that until you connect the mesh to a model, you won't see it on the screen

### Loading a texture
Textures are images to be used inside the rendering.  
Every texture is identified with a unique name.  
To create a new texture, use the method: `rm.new_texture(name, path_to_image)`

Both arguments are of type string.

Texture loading currently supports `.jpg` and `.png` formats.

### Loading a shader
Shaders are programs that run on the GPU for every vertex (vertex shder) and for every fragment (fragment shader).  
Every shader is identified with a unique name.
To create a new shader, use the method: `rm.new_shader(path_to_vert_shader, path_to_frag_shader)`

Both argument are of type string.  
Uniforms within a shader will all be stored in a dictionary inside the shader object.

### Creating a material
A material is an object that represents the color and the way that an object interacts with light.  
Every material is identified with a unique name.  
Materials contain 6 parameters that determine the look of it:
- ambient (3 floats)
- diffuse (3 floats)
- specular (3 floats)
- shininess (float)
- roughness (float)
- metallic (float)

The ambient, diffuse, specular and shininess parameters affect the look of the material in Blinn-Phong shaders.
The diffuse, roughness and metallic parameters affect the look of the material in Physically Based Rendering shaders.

To create a new material, use the method:
```python
rm.new_material(name,
                ambient_r, ambieng_g, ambient_b,
                diffuse_r, diffuse_g, diffuse_b,
                specular_r, specular_g, specular_b,
                shininess, roughness, metallic)
```
All the arguments are floats.

### Creating a model
Every model is identified with a unique name.  
Models are the 3D objects that are rendered.  
They are an object with a mesh, a texture, a shader, a material and a model matrix.

To create a new model, use the method: `rm.new_model(name, mesh, shader, texture, material)`

Each parameter is a string, for mesh, shader, texture and material, the parameter represents the name of the corresponding object.

The newly created object will be rendered with the selected mesh, shader, texture and material at the coordinates (0, 0, 0) with no rotation or scaling.



## Preview

![alt text](https://github.com/Joshua-Micheletti/Pyllium3D/blob/main/img/screenshot.png?raw=true)
