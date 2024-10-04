"""Raster Renderer module."""

# ruff: noqa: F403, F405

import glfw
from OpenGL.GL import *

from renderer.raster_renderer.raster_renderer_modules import (
    RasterBloomRenderer,
    RasterBlurRenderer,
    RasterDOFRenderer,
    RasterMSAARenderer,
    RasterSkyboxRenderer,
)
from renderer.renderer_manager.renderer_manager import MeshManager, RendererManager
from renderer.shader.shader import Shader
from utils import Singleton, Timer, get_ogl_matrix, timeit


# class to render 3D models
class RasterRenderer(metaclass=Singleton):
    """Class that implements the raster rendering pipeline.

    Args:
        metaclass (Singleton, optional): Singleton class. Defaults to Singleton.

    """

    @timeit()
    def __init__(self) -> None:
        """Set the RasterRenderer."""
        rm = RendererManager()

        self._bloom_renderer: RasterBloomRenderer = RasterBloomRenderer(rm.width, rm.height)
        self._blur_renderer: RasterBlurRenderer = RasterBlurRenderer(rm.width, rm.height)
        self._dof_renderer: RasterDOFRenderer = RasterDOFRenderer(rm.width, rm.height)
        self._msaa_renderer: RasterMSAARenderer = RasterMSAARenderer(rm.width, rm.height)
        glBindVertexArray(rm.mesh_manager._vaos['default'])
        self._skybox_renderer: RasterSkyboxRenderer = RasterSkyboxRenderer(
            'assets/textures/skybox/hdri/autumn_forest.jpg'
        )

        self._setup_opengl()
        self._setup_textures()
        self._setup_opengl_timers()
        self._last_front_frame: int = 0
        self._depth_texture: int = 0

        # timer to keep track of the rendering time
        self.timer: Timer = Timer()

    def __str__(self) -> str:
        """Handle the object as a string.

        Returns:
            str: Raster Renderer

        """
        return 'Raster Renderer'

    def __repr__(self) -> str:
        """Handle the object when printing it.

        Returns:
            str: Raster Renderer obj

        """
        return 'Raster Renderer obj'

    def _setup_opengl(self) -> None:
        """Set the OpenGL constants for rendering."""
        # set the clear color to a dark grey
        glClearColor(0.1, 0.1, 0.1, 1.0)
        # enable depth testing (hide further away triangles if covered)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        # enable face culling (don't render the inside of triangles)
        glEnable(GL_CULL_FACE)
        glEnable(GL_MULTISAMPLE)
        # enable alpha blending (transparency)
        # glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE)
        glBlendEquation(GL_FUNC_ADD)

        # enable blending on the edges of cubemap faces
        glEnable(GL_TEXTURE_CUBE_MAP_SEAMLESS)

    def _setup_textures(self) -> None:
        """Set the necessary textures for rendering."""
        # get a reference to the RendererManager
        rm: RendererManager = RendererManager()

        # method to render the brdf integration texture for light calculation
        self._render_brdf_integration_map()

        # assign texture slot 3 for the depth cubemap
        glActiveTexture(GL_TEXTURE0 + 3)
        glBindTexture(GL_TEXTURE_CUBE_MAP, rm.depth_cubemap)
        # assign texture slot 4 for the irradiance cubemap
        glActiveTexture(GL_TEXTURE0 + 4)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self._skybox_renderer.irradiance_cubemap)
        # assign texture slot 5 for the reflection cubemap
        glActiveTexture(GL_TEXTURE0 + 5)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self._skybox_renderer.reflection_cubemap)
        # assign texture slot 6 for the brdf integration texture
        glActiveTexture(GL_TEXTURE0 + 6)
        glBindTexture(GL_TEXTURE_2D, rm.brdf_integration_LUT)

    def _setup_opengl_timers(self) -> None:
        """Set OpenGL queries to keep track of performance."""
        # setup the query objects to keep track of the rendering times
        opengl_queries: any = glGenQueries(10)

        # the objects consist of a list composed of:
        # - opengl query object
        # - flag to keep track of weather to do the query or not
        # - actual value returned from the query
        self.queries: dict[str, dict] = dict(  # noqa: C418
            {
                'models': {
                    'ogl_id': opengl_queries[0],
                    'active': True,
                    'value': 0,
                },
                'instances': {
                    'ogl_id': opengl_queries[1],
                    'active': True,
                    'value': 0,
                },
                'skybox': {
                    'ogl_id': opengl_queries[2],
                    'active': True,
                    'value': 0,
                },
                'msaa': {
                    'ogl_id': opengl_queries[3],
                    'active': True,
                    'value': 0,
                },
                'bloom': {
                    'ogl_id': opengl_queries[4],
                    'active': True,
                    'value': 0,
                },
                'hdr': {
                    'ogl_id': opengl_queries[5],
                    'active': False,
                    'value': 0,
                },
                'blur': {
                    'ogl_id': opengl_queries[6],
                    'active': True,
                    'value': 0,
                },
                'depth_of_field': {
                    'ogl_id': opengl_queries[7],
                    'active': True,
                    'value': 0,
                },
                'post_processing': {
                    'ogl_id': opengl_queries[8],
                    'active': True,
                    'value': 0,
                },
                'shadow_map': {
                    'ogl_id': opengl_queries[9],
                    'active': True,
                    'value': 0,
                },
            }
        )

    # ---------------------------- Render methods ---------------------------
    # method to render the 3D models
    # @timeit(print=False)
    def render(self) -> None:
        """Render the scene.

        Pipeline steps are:
        - Shadow map
        - Standalone models
        - Instanced models
        - Skybox
        - MSAA
        - Bloom
        - Blur
        - DOF
        - Custom PostProcessing
        """
        # reference to the renderer manager
        rm: RendererManager = RendererManager()

        # -------------------- Pre-rendering --------------------------
        # render the shadow cubemap
        self._render_shadow_map()

        # -------------------- Mesh rendering -------------------------
        # bind the render framebuffer
        # if we're doing multisampling
        if rm.samples != 1:
            # bind the multisample framebuffer
            glBindFramebuffer(GL_FRAMEBUFFER, rm.render_framebuffer)
        # otherwise
        else:
            # bind the back framebuffer (?)
            glBindFramebuffer(GL_FRAMEBUFFER, rm.get_back_framebuffer())

        # clear the depth buffer
        glClear(GL_DEPTH_BUFFER_BIT)

        # draw the single models
        self._render_models()
        # and the instances
        self._render_instances()
        # render the skybox
        self._render_skybox()

        # --------------------- Post processing ----------------------
        # disable depth testing
        glDisable(GL_DEPTH_TEST)
        # bind the screen quad VAO
        glBindVertexArray(rm.mesh_manager._vaos['screen_quad'])
        # these settings are common to all post processing passes

        # solve the multisample texture
        self._render_msaa()
        # render the bloom effect (includes HDR tonemapping)
        self._render_bloom()
        # render the blur texture
        self._render_blur()
        # apply depth of field effect to the main texture
        self._render_depth_of_field()
        # apply the custom post processing effects
        # self._render_post_processing()

        # re-enable depth testing
        glEnable(GL_DEPTH_TEST)

        # bind back to the main framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        self.update_size()

        # if we're profiling the performance, get the opengl time queries
        # if rm.render_states["profile"]:
        #     self._calculate_render_times()

    # method to render the models to the render framebuffer
    def _render_models(self) -> None:
        # get a reference to the renderer manager
        rm: RendererManager = RendererManager()
        mm: MeshManager = MeshManager()

        if rm.render_states['profile']:
            glBeginQuery(GL_TIME_ELAPSED, self.queries.get('models').get('ogl_id'))

        # variables to keep track of the last used shader and mesh
        last_shader: str = ''
        last_mesh: str = ''
        last_material: str = ''
        last_texture: str = ''
        last_mesh_indices_count: int = 0
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
                last_mesh = model.mesh
                last_mesh_indices_count = mm.bind_mesh(model.mesh)

            # draw the mesh
            # glDrawArrays(GL_TRIANGLES, 0, int(rm.vertices_count[model.mesh]))
            # glBindTexture(GL_TEXTURE_CUBE_MAP, rm.depth_cubemap)
            glDrawElements(GL_TRIANGLES, last_mesh_indices_count, GL_UNSIGNED_INT, None)
            rendered_models += 1

        if rm.render_states['profile']:
            glEndQuery(GL_TIME_ELAPSED)

    # method to render instanced models
    def _render_instances(self) -> None:
        # reference to the renderer manager
        rm: RendererManager = RendererManager()

        if rm.render_states['profile']:
            glBeginQuery(GL_TIME_ELAPSED, self.queries.get('instances').get('ogl_id'))

        last_shader: str = ''

        # for every instance in the renderer manager
        for instance in rm.instances.values():
            if len(instance.models_to_render) == 0:
                continue

            if instance.shader != last_shader:
                # use the instance specific shader
                rm.shaders[instance.shader].use()
                # link the shader specific uniforms
                self._link_shader_uniforms(rm.shaders[instance.shader])

                last_shader = instance.shader

            # bind the VAO and index buffer of the mesh of the instance
            glBindVertexArray(instance.vao)
            # draw the indexed models in the instance
            glDrawElementsInstanced(
                GL_TRIANGLES,
                rm.indices_count[instance.mesh],
                GL_UNSIGNED_INT,
                None,
                len(instance.models_to_render),
            )

        if rm.render_states['profile']:
            glEndQuery(GL_TIME_ELAPSED)

    # method for rendering the shadow cubemap for point light
    def _render_shadow_map(self) -> None:
        # reference to the renderer manager
        rm: RendererManager = RendererManager()

        if not rm.render_states['shadow_map']:
            self.queries.get('shadow_map')['active'] = False
            return ()

        self.queries['shadow_map'][1] = True

        if rm.render_states['profile']:
            glBeginQuery(GL_TIME_ELAPSED, self.queries.get('shadow_map').get('ogl_id'))

        # set the viewport to match the dimensions of the shadow texture
        glViewport(0, 0, rm.shadow_size, rm.shadow_size)
        # bind the shadow framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, rm.cubemap_shadow_framebuffer)

        # clear the depth buffer bit of the shadow framebuffer
        glClear(GL_DEPTH_BUFFER_BIT)

        # use the depth cube shader
        rm.shaders['depth_cube'].use()
        # link the shader uniforms
        self._link_shader_uniforms(rm.shaders['depth_cube'])

        # keep track of the last bound mesh
        last_mesh: str = ''


        # iterate through all the models for single pass rendering
        for model in rm.single_render_models:
            # link the model specific uniforms
            self._link_model_uniforms(rm.shaders['depth_cube'], model.name)

            # check if the new model has a different mesh
            if last_mesh != model.mesh:
                # if it does, bind the new VAO
                glBindVertexArray(rm.mesh_manager._vaos[model.mesh])

                # and keep track of the last used mesh
                last_mesh = model.mesh

            # draw the mesh
            glDrawElements(GL_TRIANGLES, rm.mesh_manager._indices_count[model.mesh], GL_UNSIGNED_INT, None)

        # use the instance specific shader
        rm.shaders['depth_cube_instanced'].use()
        # link the shader specific uniforms
        self._link_shader_uniforms(rm.shaders['depth_cube_instanced'])

        # for every instance in the renderer manager
        for instance in rm.instances.values():
            # bind the VAO and index buffer of the mesh of the instance
            glBindVertexArray(instance.vao)
            # draw the indexed models in the instance
            glDrawElementsInstanced(
                GL_TRIANGLES,
                rm.indices_count[instance.mesh],
                GL_UNSIGNED_INT,
                None,
                len(instance.models),
            )

        # reset the viewport back to the rendering dimensions
        glViewport(0, 0, rm.width, rm.height)

        if rm.render_states['profile']:
            glEndQuery(GL_TIME_ELAPSED)

    # method to render the skybox
    def _render_skybox(self) -> None:
        # get a reference to the renderer manager
        rm: RendererManager = RendererManager()

        if rm.render_states['profile']:
            glBeginQuery(GL_TIME_ELAPSED, self.queries.get('skybox').get('ogl_id'))

        # bind the default mesh vao (cube)
        glBindVertexArray(rm.mesh_manager._vaos['default'])

        # set the required matrices for rendering the skybox
        self._skybox_renderer.view_matrix = get_ogl_matrix(rm.camera.center_view_matrix)

        # render the skybox
        self._skybox_renderer.render()

        if rm.render_states['profile']:
            glEndQuery(GL_TIME_ELAPSED)

    # method to resolve the msaa render texture into a single sample texture
    def _render_msaa(self) -> None:
        # reference to the renderer manager
        rm: RendererManager = RendererManager()

        if rm.samples == 1:
            self.queries['msaa'][1] = False
            return ()

        if rm.render_states['profile']:
            glBeginQuery(GL_TIME_ELAPSED, self.queries.get('msaa').get('ogl_id'))

        self._msaa_renderer.source_texture = rm.multisample_render_texture
        self._msaa_renderer.source_framebuffer = rm.render_framebuffer

        self._msaa_renderer.render()

        self._last_front_frame = self._msaa_renderer.output_texture
        self._depth_texture = self._msaa_renderer.output_depth_texture

        if rm.render_states['profile']:
            glEndQuery(GL_TIME_ELAPSED)

    # method to render the blur texture
    def _render_blur(self) -> None:
        # reference to the renderer manager
        rm: RendererManager = RendererManager()

        # set the source texture and the destination framebuffer
        self._blur_renderer.source_texture = self._last_front_frame

        # only render the blur texture if the depth of field or post processing effects are enabled
        if not rm.render_states['depth_of_field'] and not rm.render_states['post_processing']:
            self.queries.get('blur')['active'] = False
            return ()

        self.queries.get('blur')['active'] = True

        if rm.render_states['profile']:
            glBeginQuery(GL_TIME_ELAPSED, self.queries.get('blur').get('ogl_id'))

        self._blur_renderer.render()

        if rm.render_states['profile']:
            glEndQuery(GL_TIME_ELAPSED)

    # method to render the depth of field effect
    def _render_depth_of_field(self) -> None:
        # reference to renderer manager
        rm: RendererManager = RendererManager()

        # execute only if it's enabled
        if not rm.render_states['depth_of_field']:
            self.queries.get('depth_of_field')['active'] = False
            return ()

        self.queries.get('depth_of_field')['active'] = True

        if rm.render_states['profile']:
            glBeginQuery(GL_TIME_ELAPSED, self.queries.get('depth_of_field').get('ogl_id'))

        self._dof_renderer.source_texture = self._last_front_frame
        self._dof_renderer.blur_texture = self._blur_renderer.output_texture
        self._dof_renderer.depth_texture = self._depth_texture

        self._dof_renderer.render()

        self._last_front_frame = self._dof_renderer.output_texture

        if rm.render_states['profile']:
            glEndQuery(GL_TIME_ELAPSED)

    def _render_bloom(self) -> None:
        rm = RendererManager()

        # set the source texture and the destination framebuffer
        self._bloom_renderer.source_texture = self._last_front_frame
        # self._bloom_renderer.destination_framebuffer = rm.get_front_framebuffer()

        if not rm.render_states['bloom']:
            self.queries.get('bloom')['active'] = False
            self._render_hdr()
            return ()

        self.queries.get('bloom')['active'] = True

        if rm.render_states['profile']:
            glBeginQuery(GL_TIME_ELAPSED, self.queries.get('bloom').get('ogl_id'))

        self._bloom_renderer.render()

        self._last_front_frame = self._bloom_renderer.output_texture

        if rm.render_states['profile']:
            glEndQuery(GL_TIME_ELAPSED)

    def _render_hdr(self) -> None:
        rm = RendererManager()

        if rm.render_states['profile']:
            # ic(self.queries.get('hdr'))
            glBeginQuery(GL_TIME_ELAPSED, self.queries.get('hdr').get('ogl_id'))

        glBindFramebuffer(GL_FRAMEBUFFER, rm.get_front_framebuffer())

        shader = rm.shaders['hdr']
        shader.use()

        glBindTexture(GL_TEXTURE_2D, rm.get_back_texture())

        glDrawElements(GL_TRIANGLES, rm.indices_count['screen_quad'], GL_UNSIGNED_INT, None)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        if rm.render_states['profile']:
            glEndQuery(GL_TIME_ELAPSED)

    # method to render the screen texture to the main framebuffer
    def _render_screen(self) -> None:
        # bind the screen framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # get a reference to the renderer manager
        rm = RendererManager()

        # clear the color buffer
        # glClear(GL_COLOR_BUFFER_BIT)
        # disable depth testing and cull face
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)

        # use the screen shader
        rm.shaders['screen'].use()
        # bind the render framebuffer color texture
        glBindTexture(GL_TEXTURE_2D, rm.get_front_texture())

        glDrawElements(GL_TRIANGLES, rm.indices_count['screen_quad'], GL_UNSIGNED_INT, None)

        # re-enable depth testing and cull face
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

    # method to render post processing effects
    def _render_post_processing(self) -> None:
        # reference to the renderer manager
        rm = RendererManager()

        # only execute if the post processing is enabled
        if not rm.render_states['post_processing']:
            self.queries.get('post_processing')['active'] = False
            return ()

        # only execute if there are effects in the post processing list
        if len(rm.post_processing_shaders) == 0:
            self.queries.get('post_processing')['active'] = False
            return ()

        self.queries.get('post_processing')['active'] = True

        if rm.render_states['profile']:
            glBeginQuery(GL_TIME_ELAPSED, self.queries.get('post_processing').get('ogl_id'))

        # bind the screen quad mesh VAO and indices buffer
        i = 0

        # for every effect in the post processing list
        for i in range(len(rm.post_processing_shaders)):
            if i % 2 == 0:
                glBindFramebuffer(GL_FRAMEBUFFER, rm.tmp_framebuffer)
                glBindTexture(GL_TEXTURE_2D, rm.solved_texture)
            else:
                glBindFramebuffer(GL_FRAMEBUFFER, rm.solved_framebuffer)
                glBindTexture(GL_TEXTURE_2D, rm.tmp_texture)

            # use the current post processing effect
            rm.post_processing_shaders[i].use()
            # link the post processing uniforms
            self._link_post_processing_uniforms(rm.post_processing_shaders[i])
            # link the shader specific uniforms
            self._link_shader_uniforms(rm.post_processing_shaders[i])
            # link the user specific uniforms
            self._link_user_uniforms(rm.post_processing_shaders[i])

            # bind the textures to the relative texture slots
            # glActiveTexture(GL_TEXTURE0 + 0)
            # glBindTexture(GL_TEXTURE_2D, rm.solved_texture)

            glActiveTexture(GL_TEXTURE0 + 1)
            glBindTexture(GL_TEXTURE_2D, rm.blurred_texture)

            glActiveTexture(GL_TEXTURE0 + 2)
            glBindTexture(GL_TEXTURE_2D, rm.solved_depth_texture)

            # set back the active texture slot to 0
            glActiveTexture(GL_TEXTURE0)

            # render the effect
            glDrawElements(GL_TRIANGLES, rm.indices_count['screen_quad'], GL_UNSIGNED_INT, None)

        if i % 2 == 0:
            glBindFramebuffer(GL_FRAMEBUFFER, rm.solved_framebuffer)
            glBindTexture(GL_TEXTURE_2D, rm.tmp_texture)
            rm.shaders['screen'].use()
            glDrawElements(
                GL_TRIANGLES,
                int(rm.indices_count['screen_quad']),
                GL_UNSIGNED_INT,
                None,
            )

        if rm.render_states['profile']:
            glEndQuery(GL_TIME_ELAPSED)

    # method to render the brdf integration texture
    def _render_brdf_integration_map(self) -> None:
        # reference to the renderer manager
        rm = RendererManager()

        # set the viewport to the resolution of the brdf integration texture
        glViewport(0, 0, 512, 512)

        # bind the bdrf integration framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, rm.brdf_integration_framebuffer)

        # use the brdf integration shader
        shader = rm.shaders['brdf_integration']
        shader.use()

        # clear the texture
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # draw the quad
        glBindVertexArray(rm.mesh_manager._vaos['screen_quad'])
        glDrawElements(GL_TRIANGLES, rm.mesh_manager._indices_count['screen_quad'], GL_UNSIGNED_INT, None)

        # set the viewport back to its original dimensions
        glViewport(0, 0, rm.width, rm.height)

    # ---------------------------- Link methods ----------------------------
    # method to link static uniforms to the shader (static meaning they don't change between meshes)
    def _link_shader_uniforms(self, shader: Shader) -> None:
        # get a reference to the renderer manager
        rm = RendererManager()

        if 'view' in shader.uniforms:
            glUniformMatrix4fv(shader.uniforms['view'], 1, GL_FALSE, get_ogl_matrix(rm.camera.view_matrix))
        if 'projection' in shader.uniforms:
            glUniformMatrix4fv(
                shader.uniforms['projection'],
                1,
                GL_FALSE,
                rm.get_ogl_projection_matrix(),
            )
        if 'light' in shader.uniforms:
            glUniform3f(
                shader.uniforms['light'],
                rm.light_positions[0],
                rm.light_positions[1],
                rm.light_positions[2],
            )
        if 'eye' in shader.uniforms:
            glUniform3f(
                shader.uniforms['eye'],
                rm.camera.position.x,
                rm.camera.position.y,
                rm.camera.position.z,
            )

        if 'skybox_view' in shader.uniforms:
            glUniformMatrix4fv(
                shader.uniforms['skybox_view'],
                1,
                GL_FALSE,
                rm.camera.get_skybox_ogl_matrix(),
            )

        light_material = rm.light_material()

        if 'light_ambient' in shader.uniforms:
            glUniform3f(
                shader.uniforms['light_ambient'],
                light_material.ambient[0],
                light_material.ambient[1],
                light_material.ambient[2],
            )
        if 'light_diffuse' in shader.uniforms:
            glUniform3f(
                shader.uniforms['light_diffuse'],
                light_material.diffuse[0],
                light_material.diffuse[1],
                light_material.diffuse[2],
            )
        if 'light_specular' in shader.uniforms:
            glUniform3f(
                shader.uniforms['light_specular'],
                light_material.specular[0],
                light_material.specular[1],
                light_material.specular[2],
            )
        if 'light_color' in shader.uniforms:
            glUniform3f(
                shader.uniforms['light_color'],
                light_material.diffuse[0],
                light_material.diffuse[1],
                light_material.diffuse[2],
            )
        if 'light_strength' in shader.uniforms:
            glUniform1f(shader.uniforms['light_strength'], rm.light_strengths[0])

        if 'lights' in shader.uniforms:
            glUniform3fv(shader.uniforms['lights'], rm.lights_count, rm.light_positions)

        if 'light_colors' in shader.uniforms:
            glUniform3fv(shader.uniforms['light_colors'], rm.lights_count, rm.light_colors)

        if 'light_strengths' in shader.uniforms:
            glUniform1fv(shader.uniforms['light_strengths'], rm.lights_count, rm.light_strengths)

        if 'lights_count' in shader.uniforms:
            glUniform1f(shader.uniforms['lights_count'], rm.lights_count)

        if 'screen_texture' in shader.uniforms:
            glUniform1i(shader.uniforms['screen_texture'], 0)
        if 'blurred_texture' in shader.uniforms:
            glUniform1i(shader.uniforms['blurred_texture'], 1)
        if 'depth_texture' in shader.uniforms:
            glUniform1i(shader.uniforms['depth_texture'], 2)

        if 'depth_map' in shader.uniforms:
            glUniform1i(shader.uniforms['depth_map'], 3)
        if 'irradiance_map' in shader.uniforms:
            glUniform1i(shader.uniforms['irradiance_map'], 4)
        if 'reflection_map' in shader.uniforms:
            glUniform1i(shader.uniforms['reflection_map'], 5)
        if 'brdf_integration' in shader.uniforms:
            glUniform1i(shader.uniforms['brdf_integration'], 6)

        if 'samples' in shader.uniforms:
            glUniform1i(shader.uniforms['samples'], rm.samples)

        if 'cube_matrices' in shader.uniforms:
            shadow_matrices = rm.get_ogl_shadow_matrices()
            for i in range(6):
                glUniformMatrix4fv(
                    shader.uniforms['cube_matrices'] + i,
                    1,
                    GL_FALSE,
                    shadow_matrices[i],
                )

        if 'far_plane' in shader.uniforms:
            glUniform1f(shader.uniforms['far_plane'], rm.shadow_far_plane)
        # if "cube_matrices" in shader.uniforms:
        #     glUniformMatrix4fv(shader.uniforms["cube_matrices[0]"], rm.)

    # method to link dynamic uniforms to the shader (dynamic meaning they change between meshes)
    def _link_model_uniforms(self, shader, name) -> None:
        rm = RendererManager()

        if 'model' in shader.uniforms:
            glUniformMatrix4fv(shader.uniforms['model'], 1, GL_FALSE, rm.get_ogl_matrix(name))

    def _link_material_uniforms(self, shader, name) -> None:
        rm = RendererManager()
        model = rm.models[name]

        if 'ambient' in shader.uniforms:
            glUniform3f(
                shader.uniforms['ambient'],
                rm.materials[model.material].ambient[0],
                rm.materials[model.material].ambient[1],
                rm.materials[model.material].ambient[2],
            )
        if 'diffuse' in shader.uniforms:
            glUniform3f(
                shader.uniforms['diffuse'],
                rm.materials[model.material].diffuse[0],
                rm.materials[model.material].diffuse[1],
                rm.materials[model.material].diffuse[2],
            )
        if 'specular' in shader.uniforms:
            glUniform3f(
                shader.uniforms['specular'],
                rm.materials[model.material].specular[0],
                rm.materials[model.material].specular[1],
                rm.materials[model.material].specular[2],
            )
        if 'shininess' in shader.uniforms:
            glUniform1f(shader.uniforms['shininess'], rm.materials[model.material].shininess)
        if 'albedo' in shader.uniforms:
            glUniform3f(
                shader.uniforms['albedo'],
                rm.materials[model.material].diffuse[0],
                rm.materials[model.material].diffuse[1],
                rm.materials[model.material].diffuse[2],
            )
        if 'roughness' in shader.uniforms:
            glUniform1f(shader.uniforms['roughness'], rm.materials[model.material].roughness)
        if 'metallic' in shader.uniforms:
            glUniform1f(shader.uniforms['metallic'], rm.materials[model.material].metallic)

    def _link_post_processing_uniforms(self, shader) -> None:
        if 'time' in shader.uniforms:
            glUniform1f(shader.uniforms['time'], glfw.get_time() * 10)

    def _link_user_uniforms(self, shader) -> None:
        if 'user_distance' in shader.uniforms:
            glUniform1f(shader.uniforms['user_distance'], shader.user_uniforms['user_distance'])
        if 'user_range' in shader.uniforms:
            glUniform1f(shader.uniforms['user_range'], shader.user_uniforms['user_range'])
        if 'user_parameter_0' in shader.uniforms:
            glUniform1f(
                shader.uniforms['user_parameter_0'],
                shader.user_uniforms['user_parameter_0'],
            )
        if 'user_parameter_1' in shader.uniforms:
            glUniform1f(
                shader.uniforms['user_parameter_1'],
                shader.user_uniforms['user_parameter_1'],
            )
        if 'user_parameter_2' in shader.uniforms:
            glUniform1f(
                shader.uniforms['user_parameter_2'],
                shader.user_uniforms['user_parameter_2'],
            )
        if 'user_parameter_3' in shader.uniforms:
            glUniform1f(
                shader.uniforms['user_parameter_3'],
                shader.user_uniforms['user_parameter_3'],
            )

    def _calculate_render_times(self) -> None:
        for _name, query in self.queries.items():
            if not query.get('active'):
                query['value'] = 0
                continue

            available = GLuint(0)

            while not available:
                glGetQueryObjectiv(query.get('ogl_id'), GL_QUERY_RESULT_AVAILABLE, available)

            # result = np.array([0], dtype=np.int32)

            elapsed_time = GLuint64(0)
            glGetQueryObjectui64v(query.get('ogl_id'), GL_QUERY_RESULT, ctypes.byref(elapsed_time))

            query['value'] = elapsed_time.value / 1000000

    def update_size(self) -> None:
        """Update the dimensions of the renderers."""
        rm = RendererManager()
        self._bloom_renderer.update_size(rm.width, rm.height)
        self._blur_renderer.update_size(rm.width, rm.height)
        self._dof_renderer.update_size(rm.width, rm.height)
        self._msaa_renderer.update_size(rm.width, rm.height)
        self._skybox_renderer.update_size(rm.width, rm.height)

    @property
    def last_front_frame(self) -> int:
        """Get the last rendered frame."""
        return self._last_front_frame
