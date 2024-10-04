"""Raster model renderer."""

class RasterModelRenderer:
    """Class to render 3D models."""
    
    def __init__(self) -> None:
        print("hello")
        
    def render(self, models, meshes, materials, textures, shaders) -> None:
        """Render the models.
        
        Args:
            models (_type_): _description_
            meshes (_type_): _description_
            materials (_type_): _description_
            textures (_type_): _description_
            shaders (_type_): _description_

        """
        # variables to keep track of the last used shader and mesh
        last_shader: str = ''
        last_mesh: str = ''
        last_material: str = ''
        last_texture: str = ''
        rendered_models: int = 0

        # THIS LOOP WILL CHANGE WHEN THE MODELS WILL BE GROUPED BY SHADER, SO THAT THERE ISN'T SO MUCH CONTEXT SWITCHING
        # for every model in the renderer manager
        for model in rm.single_render_models:
            if not rm.check_visibility(model.name):
                continue

            # check if the new model has a different shader
            if last_shader != model.shader:
                # if it has a different shader, change to the current shader
                rm.shaders[model.shader].use()
                # link the static uniforms (that don't change between meshes)
                self._link_shader_uniforms(rm.shaders[model.shader])
                # keep track of the last set shader
                last_shader = model.shader

            # check if the new model has a different material
            if last_material != model.material:
                # link the corresponding uniforms
                self._link_material_uniforms(rm.shaders[model.shader], model.name)
                # keep track of the last used material
                last_material = model.material

            if last_texture != model.texture and model.texture is None:
                glBindTexture(GL_TEXTURE_2D, rm.textures[model.texture])
                last_texture = model.texture

            # link the model specific uniforms
            self._link_model_uniforms(rm.shaders[model.shader], model.name)

            # check if the new model has a different mesh
            if last_mesh != model.mesh:
                # if it does, bind the new VAO
                glBindVertexArray(rm.vaos[model.mesh])
                # and keep track of the last used mesh
                last_mesh = model.mesh

            # draw the mesh
            # glDrawArrays(GL_TRIANGLES, 0, int(rm.vertices_count[model.mesh]))
            # glBindTexture(GL_TEXTURE_CUBE_MAP, rm.depth_cubemap)
            glDrawElements(GL_TRIANGLES, int(rm.indices_count[model.mesh]), GL_UNSIGNED_INT, None)
            rendered_models += 1

        if rm.render_states['profile']:
            glEndQuery(GL_TIME_ELAPSED)