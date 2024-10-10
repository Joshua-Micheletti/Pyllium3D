"""Raster forward model renderer."""

# ruff: noqa: F403, F405

from OpenGL.GL import *

from renderer.material.material import Material
from renderer.model.model import Model
from renderer.shader.shader import Shader


class RasterForwardModelRenderer:
    """Class to render 3D models with forward rendering."""

    def __init__(self) -> None:
        print('hello')

    def render(
        self,
        models: dict[str, Model],
        model_matrices: dict[str, any],
        materials: dict[str, Material],
        meshes: dict[str, int],
        indices_counts: dict[str, int],
        textures: dict[str, int],
        shaders: dict[str, Shader],
        view_matrix: any,
        projection_matrix: any,
    ) -> None:
        """Render the models.

        Args:
            models (dict[str, Model]): Dictionary of models to render
            meshes (dict[str, int]): Dictionary of available meshes
            materials (dict[str, Material]): Dictionary of available materials
            textures (dict[str, int]): Dictionary of available textures
            shaders (dict[str, Shader]): Dictionary of available shaders

        """
        # variables to keep track of the last used shader and mesh
        last_shader: str = ''
        shader: Shader = None
        last_mesh: str = ''
        last_material: str = ''
        last_texture: str = ''
        # rendered_models: int = 0

        # THIS LOOP WILL CHANGE WHEN THE MODELS WILL BE GROUPED BY SHADER, SO THAT THERE ISN'T SO MUCH CONTEXT SWITCHING
        # for every model in the renderer manager
        for model in models:
            # FRUSTUM CULLING
            # if not rm.check_visibility(model.name):
            #     continue

            # check if the new model has a different shader
            if last_shader != model.shader:
                # get a reference to the shader to use
                shader = shaders.get(model.shader)
                # if it has a different shader, change to the current shader
                shader.use()
                # link the static uniforms (that don't change between meshes)
                # self._link_shader_uniforms(shaders[model.shader])
                shader.bind_uniform('view', view_matrix)
                shader.bind_uniform('projection', projection_matrix)

                # keep track of the last set shader
                last_shader = model.shader

            # check if the new model has a different material
            if last_material != model.material:
                # link the corresponding uniforms
                self._link_material_uniforms(shaders[model.shader], model.name)
                # keep track of the last used material
                last_material = model.material

            if last_texture != model.texture and model.texture is None:
                glBindTexture(GL_TEXTURE_2D, textures[model.texture])
                last_texture = model.texture

            # link the model specific uniforms
            shader.bind_uniform('model', model_matrices.get(model.name))

            # check if the new model has a different mesh
            if last_mesh != model.mesh:
                # if it does, bind the new VAO
                glBindVertexArray(meshes[model.mesh])
                # and keep track of the last used mesh
                last_mesh = model.mesh

            # draw the mesh
            # glDrawArrays(GL_TRIANGLES, 0, int(rm.vertices_count[model.mesh]))
            # glBindTexture(GL_TEXTURE_CUBE_MAP, rm.depth_cubemap)
            glDrawElements(GL_TRIANGLES, int(indices_counts[model.mesh]), GL_UNSIGNED_INT, None)
            # rendered_models += 1
