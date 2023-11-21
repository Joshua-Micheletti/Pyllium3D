from utils.singleton import Singleton
from OpenGL.GL import *
import numpy as np
import glm
import glfw

from utils.timer import Timer
from renderer.renderer_manager import RendererManager

# class to render 3D models
class Renderer(metaclass=Singleton):
    # constructor method
    def __init__(self):
        # set the clear color to a dark grey
        glClearColor(0.1, 0.1, 0.1, 1.0)
        # enable depth testing (hide further away triangles if covered)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        # enable face culling (don't render the inside of triangles)
        glEnable(GL_CULL_FACE)
        glEnable(GL_MULTISAMPLE)
        # enable alpha blending (transparency)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_TEXTURE_CUBE_MAP_SEAMLESS)

        # method to render the skybox from an equirect to a cubemap
        self._render_equirectangular_skybox()
        # method to render the irradiance cubemap for light calculation
        self._render_irradiance_map()
        # method to render the brdf integration texture for light calculation
        self._render_brdf_integration_map()
        # method to render the reflection cubemap
        self._render_reflection_map()

        # timer to keep track of the rendering time
        self.timer = Timer()

    # ---------------------------- Render methods ---------------------------
    # method to render the 3D models
    def render(self):
        # reset the timer
        self.timer.reset()

        # reference to the renderer manager
        rm = RendererManager()

        # check if the shadow map should be draw
        if rm.render_states["shadow_map"]:
            # render the shadow cubemap
            self._render_shadow_map()

        # bind the render framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, rm.render_framebuffer)
        # clear the framebuffer and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # draw the single models 
        self._render_models()
        # and the instances
        self._render_instances()

        # render the skybox
        self._render_skybox()

        self._render_msaa()

        self._render_bloom()
        # render the blur texture
        self._render_blur()
        # apply depth of field effect to the main texture
        self._render_depth_of_field()
        # apply post processing effects
        self._render_post_processing()

        # clear the screen
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        # clear the color buffer
        glClear(GL_COLOR_BUFFER_BIT)

        # record the time it took to render in the timer
        self.timer.record()
        
    # method to render the models to the render framebuffer
    def _render_models(self):
        # get a reference to the renderer manager
        rm = RendererManager()   
        
        # variables to keep track of the last used shader and mesh
        last_shader = ""
        last_mesh = ""
        last_material = ""
        last_texture = ""

        glActiveTexture(GL_TEXTURE0 + 3)
        glBindTexture(GL_TEXTURE_CUBE_MAP, rm.depth_cubemap)

        glActiveTexture(GL_TEXTURE0 + 4)
        glBindTexture(GL_TEXTURE_CUBE_MAP, rm.irradiance_cubemap)

        glActiveTexture(GL_TEXTURE0 + 5)
        glBindTexture(GL_TEXTURE_CUBE_MAP, rm.reflection_map)

        glActiveTexture(GL_TEXTURE0 + 6)
        glBindTexture(GL_TEXTURE_2D, rm.brdf_integration_LUT)

        glActiveTexture(GL_TEXTURE0)

        
        # THIS LOOP WILL CHANGE WHEN THE MODELS WILL BE GROUPED BY SHADER, SO THAT THERE ISN'T SO MUCH CONTEXT SWITCHING
        # for every model in the renderer manager
        for model in rm.single_render_models:
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

            if last_texture != model.texture:
                if model.texture != None:
                    glBindTexture(GL_TEXTURE_2D, rm.textures[model.texture])
                    last_texture = model.texture

            # link the model specific uniforms
            self._link_model_uniforms(rm.shaders[model.shader], model.name)

            # check if the new model has a different mesh
            if last_mesh != model.mesh:
                # if it does, bind the new VAO
                
                glBindVertexArray(rm.vaos[model.mesh])
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, rm.ebos[model.mesh])
                
                # and keep track of the last used mesh
                last_mesh = model.mesh

            # draw the mesh
            # glDrawArrays(GL_TRIANGLES, 0, int(rm.vertices_count[model.mesh]))
            # glBindTexture(GL_TEXTURE_CUBE_MAP, rm.depth_cubemap)
            glDrawElements(GL_TRIANGLES, int(rm.indices_count[model.mesh]), GL_UNSIGNED_INT, None)

            glEnable(GL_CULL_FACE)

    # method to render instanced models
    def _render_instances(self):
        # reference to the renderer manager
        rm = RendererManager()

        glActiveTexture(GL_TEXTURE0 + 3)
        glBindTexture(GL_TEXTURE_CUBE_MAP, rm.depth_cubemap)

        glActiveTexture(GL_TEXTURE0 + 4)
        glBindTexture(GL_TEXTURE_CUBE_MAP, rm.irradiance_cubemap)

        glActiveTexture(GL_TEXTURE0 + 5)
        glBindTexture(GL_TEXTURE_CUBE_MAP, rm.reflection_map)

        glActiveTexture(GL_TEXTURE0 + 6)
        glBindTexture(GL_TEXTURE_2D, rm.brdf_integration_LUT)

        # for every instance in the renderer manager
        for instance in rm.instances.values():
            # use the instance specific shader
            rm.shaders[instance.shader].use()
            # link the shader specific uniforms
            self._link_shader_uniforms(rm.shaders[instance.shader])
            
            # bind the VAO and index buffer of the mesh of the instance
            glBindVertexArray(instance.vao)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, rm.ebos[instance.mesh])
            # draw the indexed models in the instance
            glDrawElementsInstanced(GL_TRIANGLES, int(rm.indices_count[instance.mesh]), GL_UNSIGNED_INT, None, len(instance.models))

        glActiveTexture(GL_TEXTURE0)

    # method for rendering the shadow cubemap for point light
    def _render_shadow_map(self):
        # reference to the renderer manager
        rm = RendererManager()

        # set the viewport to match the dimensions of the shadow texture
        glViewport(0, 0, rm.shadow_size, rm.shadow_size)
        # bind the shadow framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, rm.cubemap_shadow_framebuffer)

        # clear the depth buffer bit of the shadow framebuffer
        glClear(GL_DEPTH_BUFFER_BIT)

        # use the depth cube shader
        rm.shaders["depth_cube"].use()
        # link the shader uniforms
        self._link_shader_uniforms(rm.shaders["depth_cube"])

        # keep track of the last bound mesh
        last_mesh = ""

        # iterate through all the models for single pass rendering
        for model in rm.single_render_models:
            # link the model specific uniforms
            self._link_model_uniforms(rm.shaders["depth_cube"], model.name)

            # check if the new model has a different mesh
            if last_mesh != model.mesh:
                # if it does, bind the new VAO
                glBindVertexArray(rm.vaos[model.mesh])
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, rm.ebos[model.mesh])
                
                # and keep track of the last used mesh
                last_mesh = model.mesh

            # draw the mesh
            glDrawElements(GL_TRIANGLES, int(rm.indices_count[model.mesh]), GL_UNSIGNED_INT, None)


        # use the instance specific shader
        rm.shaders["depth_cube_instanced"].use()
        # link the shader specific uniforms
        self._link_shader_uniforms(rm.shaders["depth_cube_instanced"])

        # for every instance in the renderer manager
        for instance in rm.instances.values():
            # bind the VAO and index buffer of the mesh of the instance
            glBindVertexArray(instance.vao)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, rm.ebos[instance.mesh])
            # draw the indexed models in the instance
            glDrawElementsInstanced(GL_TRIANGLES, int(rm.indices_count[instance.mesh]), GL_UNSIGNED_INT, None, len(instance.models))

        # reset the viewport back to the rendering dimensions
        glViewport(0, 0, rm.width, rm.height)

    # method to render the skybox
    def _render_skybox(self):
        # get a reference to the renderer manager
        rm = RendererManager()

        # use the skybox shader
        rm.shaders["skybox"].use()

        # temporarily place the camera at the origin, to cancel camera movement from the skybox rendering
        old_position = rm.camera.position
        rm.camera.place(0, 0, 0)
        self._link_shader_uniforms(rm.shaders["skybox"])
        rm.camera.place(old_position.x, old_position.y, old_position.z)

        # bind the default mesh vao (cube)
        glBindVertexArray(rm.vaos["default"])
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, rm.ebos["default"])

        # disable cull facing
        glDisable(GL_CULL_FACE)
        # bind the skybox cubemap texture
        glBindTexture(GL_TEXTURE_CUBE_MAP, rm.skybox_texture)
        # glBindTexture(GL_TEXTURE_CUBE_MAP, rm.depth_cubemap)
        # glBindTexture(GL_TEXTURE_CUBE_MAP, rm.irradiance_cubemap)
        # glBindTexture(GL_TEXTURE_CUBE_MAP, rm.reflection_map)
        # render the cube
        glDrawElements(GL_TRIANGLES, rm.indices_count["default"], GL_UNSIGNED_INT, None)
        # re-enable face culling
        glEnable(GL_CULL_FACE)

    # method to resolve the msaa render texture into a single sample texture
    def _render_msaa(self):
        # reference to the renderer manager
        rm = RendererManager()

        # disable depth testing
        glDisable(GL_DEPTH_TEST)

        # bind the solved framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, rm.solved_framebuffer)
        # bind the multisample texture to resolve
        glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, rm.multisample_render_texture)

        # bind the screen quad mesh VAO
        glBindVertexArray(rm.vaos["screen_quad"])
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, rm.ebos["screen_quad"])

        # use the msaa shader
        rm.shaders["msaa"].use()
        self._link_shader_uniforms(rm.shaders["msaa"])

        # render the multisample texture into the new solved texture applying anti-aliasing
        glDrawElements(GL_TRIANGLES, rm.indices_count["screen_quad"], GL_UNSIGNED_INT, None)

        # resolve the depth buffer through nearest filtering
        glBindFramebuffer(GL_READ_FRAMEBUFFER, rm.render_framebuffer)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, rm.solved_framebuffer)
        glBlitFramebuffer(0, 0, rm.width, rm.height, 0, 0, rm.width, rm.height, GL_DEPTH_BUFFER_BIT, GL_NEAREST)

        # re-enable depth testing
        glEnable(GL_DEPTH_TEST)

    # method to render the blur texture
    def _render_blur(self):
        # reference to the renderer manager
        rm = RendererManager()

        # only render the blur texture if the depth of field or post processing effects are enabled
        if not rm.render_states["depth_of_field"] and not rm.render_states["post_processing"]:
            return()

        # bind the blurred framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, rm.blurred_framebuffer)
        # clear the blur texture
        glClear(GL_COLOR_BUFFER_BIT)

        # disable depth testing
        glDisable(GL_DEPTH_TEST)
        # bind the screen quad mesh VAO and indices
        glBindVertexArray(rm.vaos["screen_quad"])
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, rm.ebos["screen_quad"])
        # use the blur shader
        rm.shaders["post_processing/blur"].use()
        # bind the color texture as source
        glBindTexture(GL_TEXTURE_2D, rm.solved_texture)

        # draw the blurred image
        glDrawElements(GL_TRIANGLES, rm.indices_count["screen_quad"], GL_UNSIGNED_INT, None)

        # bind the blurred texture as source
        glBindTexture(GL_TEXTURE_2D, rm.blurred_texture)

        # bind the temporary framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, rm.tmp_framebuffer)
        # blur the image again
        glDrawElements(GL_TRIANGLES, rm.indices_count["screen_quad"], GL_UNSIGNED_INT, None)

        # bind the blurred framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, rm.blurred_framebuffer)
        # bind the temporary texture as source
        glBindTexture(GL_TEXTURE_2D, rm.tmp_texture)

        # use the dilation shader
        rm.shaders["post_processing/dilation"].use()
        # render the dilated texture
        glDrawElements(GL_TRIANGLES, rm.indices_count["screen_quad"], GL_UNSIGNED_INT, None)

        # re-enable depth testing
        glEnable(GL_DEPTH_TEST)

    # method to render the depth of field effect
    def _render_depth_of_field(self):
        # reference to renderer manager
        rm = RendererManager()

        # execute only if it's enabled
        if not rm.render_states["depth_of_field"]:
            return()

        # disable depth testing
        glDisable(GL_DEPTH_TEST)
        # bind the main render framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, rm.solved_framebuffer)
        
        # use the depth of field shader
        rm.shaders["depth_of_field"].use()
        # link the shader specific uniforms
        self._link_shader_uniforms(rm.shaders["depth_of_field"])

        # bind the required textures to the correct texture slots
        glActiveTexture(GL_TEXTURE0 + 0)
        glBindTexture(GL_TEXTURE_2D, rm.solved_texture)

        glActiveTexture(GL_TEXTURE0 + 1)
        glBindTexture(GL_TEXTURE_2D, rm.blurred_texture)

        glActiveTexture(GL_TEXTURE0 + 2)
        glBindTexture(GL_TEXTURE_2D, rm.solved_depth_texture)

        # draw the scene with depth of field
        glDrawElements(GL_TRIANGLES, int(rm.indices_count["screen_quad"]), GL_UNSIGNED_INT, None)

        # set back the active texture slot to index 0
        glActiveTexture(GL_TEXTURE0)
        # re-enable depth testing
        glEnable(GL_DEPTH_TEST)

    def _render_bloom(self):
        rm = RendererManager()
        glDisable(GL_DEPTH_TEST)

        if not rm.render_states["bloom"]:
            return()
        
        glBindFramebuffer(GL_FRAMEBUFFER, rm.bloom_framebuffer)

        # DOWNSAMPLE
        glBindTexture(GL_TEXTURE_2D, rm.solved_texture)

        shader = rm.shaders["bloom_downsample"]
        shader.use()
        glUniform2f(shader.uniforms["src_resolution"], rm.width, rm.height)

        glBindVertexArray(rm.vaos["screen_quad"])
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, rm.ebos["screen_quad"])

        for i in range(len(rm.bloom_mips)):
            glViewport(0, 0, rm.bloom_mips_sizes[i][0], rm.bloom_mips_sizes[i][1])
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, rm.bloom_mips[i], 0)

            glDrawElements(GL_TRIANGLES, rm.indices_count["screen_quad"], GL_UNSIGNED_INT, None)

            glUniform2f(shader.uniforms["src_resolution"], rm.bloom_mips_sizes[i][0], rm.bloom_mips_sizes[i][1])
            glBindTexture(GL_TEXTURE_2D, rm.bloom_mips[i])

        # UPSAMPLE
        shader = rm.shaders["bloom_upsample"]
        shader.use()

        # glUniform1f(shader.uniforms["radius"], 2.0)

        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE)
        glBlendEquation(GL_FUNC_ADD)

        for i in range(len(rm.bloom_mips) - 1, 0, -1):
            current_mip = rm.bloom_mips[i]
            next_mip = rm.bloom_mips[i - 1]
            next_mip_size = rm.bloom_mips_sizes[i - 1]

            glBindTexture(GL_TEXTURE_2D, current_mip)

            glViewport(0, 0, next_mip_size[0], next_mip_size[1])
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, next_mip, 0)

            glDrawElements(GL_TRIANGLES, rm.indices_count["screen_quad"], GL_UNSIGNED_INT, None)

        glViewport(0, 0, rm.width, rm.height)
        glDisable(GL_BLEND)

        # BLENDING
        glBindFramebuffer(GL_FRAMEBUFFER, rm.tmp_framebuffer)

        shader = rm.shaders["bloom"]
        shader.use()

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, rm.solved_texture)
        glActiveTexture(GL_TEXTURE0 + 1)
        glBindTexture(GL_TEXTURE_2D, rm.bloom_mips[0])

        glDrawElements(GL_TRIANGLES, rm.indices_count["screen_quad"], GL_UNSIGNED_INT, None)
        # glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glActiveTexture(GL_TEXTURE0)
        glBindFramebuffer(GL_FRAMEBUFFER, rm.solved_framebuffer)
        glBindTexture(GL_TEXTURE_2D, rm.tmp_texture)
        rm.shaders["screen"].use()
        glDrawElements(GL_TRIANGLES, rm.indices_count["screen_quad"], GL_UNSIGNED_INT, None)

        # glBindFramebuffer(GL_FRAMEBUFFER, rm.tmp_framebuffer)
        # glClear(GL_COLOR_BUFFER_BIT)

        glDisable(GL_BLEND)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glActiveTexture(GL_TEXTURE0)

        glEnable(GL_DEPTH_TEST)


    # method to render the screen texture to the main framebuffer
    def _render_screen(self):
        # bind the screen framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # get a reference to the renderer manager
        rm = RendererManager()

        # clear the color buffer
        glClear(GL_COLOR_BUFFER_BIT)
        # disable depth testing and cull face
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        
        # use the screen shader
        rm.shaders["screen"].use()
        # bind the screen quad VAO
        glBindVertexArray(rm.vaos["screen_quad"])
        # bind the render framebuffer color texture
        glBindTexture(GL_TEXTURE_2D, rm.color_render_texture)
        # draw the quad with the texture
        glDrawArrays(GL_TRIANGLES, 0, 6)

        # re-enable depth testing and cull face
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

    # method to render post processing effects
    def _render_post_processing(self):
        # reference to the renderer manager
        rm = RendererManager()

        # only execute if the post processing is enabled
        if not rm.render_states["post_processing"]:
            return()
        
        # only execute if there are effects in the post processing list
        if len(rm.post_processing_shaders) == 0:
            return()
    
        # disable depth testing
        glDisable(GL_DEPTH_TEST)
    
        # bind the screen quad mesh VAO and indices buffer
        glBindVertexArray(rm.vaos["screen_quad"])
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, rm.ebos["screen_quad"])

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
            glDrawElements(GL_TRIANGLES, int(rm.indices_count["screen_quad"]), GL_UNSIGNED_INT, None)

        if i % 2 == 0:
            glBindFramebuffer(GL_FRAMEBUFFER, rm.solved_framebuffer)
            glBindTexture(GL_TEXTURE_2D, rm.tmp_texture)
            rm.shaders["screen"].use()
            glDrawElements(GL_TRIANGLES, int(rm.indices_count["screen_quad"]), GL_UNSIGNED_INT, None)

        # re-enable depth testing
        glEnable(GL_DEPTH_TEST)

    # method to render the irradiance cubemap of the skybox
    def _render_irradiance_map(self):
        # reference to the renderer manager
        rm = RendererManager()

        # set the viewport to the dimensions of the irradiance map size
        glViewport(0, 0, rm.irradiance_map_size, rm.irradiance_map_size)
        # bind the irradiance framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, rm.irradiance_framebuffer)

        # use the irradiance cubemap shader
        shader = rm.shaders["irradiance_cube"]
        shader.use()

        # bind the cubemap projection matrix to the projection uniform
        glUniformMatrix4fv(shader.uniforms["projection"], 1, GL_FALSE, glm.value_ptr(rm.cubemap_projection))

        # bind the cube mesh VAO
        glBindVertexArray(rm.vaos["default"])
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, rm.ebos["default"])

        # bind the skybox texture cubemap as source
        glBindTexture(GL_TEXTURE_CUBE_MAP, rm.skybox_texture)

        # disable face culling
        glDisable(GL_CULL_FACE)

        # iterate through all the faces of the cubemap
        for i in range(6):
            # update the view matrix
            glUniformMatrix4fv(shader.uniforms["view"], 1, GL_FALSE, glm.value_ptr(rm.center_cubemap_views[i]))
            # update the framebuffer color attachment texture with the correct cubemap texture
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, rm.irradiance_cubemap, 0)
            # clear the texture
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            # draw the irradiance texture
            glDrawElements(GL_TRIANGLES, rm.indices_count["default"], GL_UNSIGNED_INT, None)
        
        # re-enable backface culling
        glEnable(GL_CULL_FACE)

        # restore the viewport to the render dimensions
        glViewport(0, 0, rm.width, rm.height)

    # method to render an equirect skybox into a cubemap
    def _render_equirectangular_skybox(self):
        # reference to the renderer manager
        rm = RendererManager()

        # if there isn't an equirect skybox set, return immediately
        if rm.equirect_skybox is None:
            return()

        # set the viewport to the skybox dimensions
        glViewport(0, 0, rm.skybox_resolution, rm.skybox_resolution)
        # bind the skybox framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, rm.skybox_framebuffer)

        # use the equirect skybox shader
        shader = rm.shaders["equirect_skybox"]
        shader.use()

        # set the projection uniform to the cubemap projection
        glUniformMatrix4fv(shader.uniforms["projection"], 1, GL_FALSE, glm.value_ptr(rm.cubemap_projection))

        # bind the cube mesh VAO
        glBindVertexArray(rm.vaos["default"])
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, rm.ebos["default"])

        # bind the source equirect skybox texture
        glBindTexture(GL_TEXTURE_2D, rm.equirect_skybox)

        # disable backface culling
        glDisable(GL_CULL_FACE)

        # iterate through every face
        for i in range(6):
            # update the view matrix accordingly
            glUniformMatrix4fv(shader.uniforms["view"], 1, GL_FALSE, glm.value_ptr(rm.center_cubemap_views[i]))
            # bind the texture target of the framebuffer accordingly
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, rm.skybox_texture, 0)
            # clear the previous texture
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # draw the face to the cubemap
            glDrawElements(GL_TRIANGLES, rm.indices_count["default"], GL_UNSIGNED_INT, None)

        # re-enable backface culling
        glEnable(GL_CULL_FACE)
        # set the viewport back to the render size
        glViewport(0, 0, rm.width, rm.height)

    # method to render the brdf integration texture
    def _render_brdf_integration_map(self):
        # reference to the renderer manager
        rm = RendererManager()

        # set the viewport to the resolution of the brdf integration texture
        glViewport(0, 0, 512, 512)

        # bind the bdrf integration framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, rm.brdf_integration_framebuffer)

        # bind the screen quad mesh VAO
        glBindVertexArray(rm.vaos["screen_quad"])
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, rm.ebos["screen_quad"])

        # use the brdf integration shader
        shader = rm.shaders["brdf_integration"]
        shader.use()

        # clear the texture
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # draw the quad
        glDrawElements(GL_TRIANGLES, rm.indices_count["screen_quad"], GL_UNSIGNED_INT, None)

        # set the viewport back to its original dimensions
        glViewport(0, 0, rm.width, rm.height)

    # method to render the reflection cubemap with its mipmap levels
    def _render_reflection_map(self):
        # reference to the renderer manager
        rm = RendererManager()

        # bind the reflection framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, rm.reflection_framebuffer)
        
        # use the reflection prefilter shader
        shader = rm.shaders["reflection_prefilter"]
        shader.use()

        # bind the projection matrix uniform to the cubemap projection matrix
        glUniformMatrix4fv(shader.uniforms["projection"], 1, GL_FALSE, glm.value_ptr(rm.cubemap_projection))

        # bind the cube mesh VAO
        glBindVertexArray(rm.vaos["default"])
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, rm.ebos["default"])

        # bind the skybox texture as source
        glBindTexture(GL_TEXTURE_CUBE_MAP, rm.skybox_texture)

        # disable backface culling
        glDisable(GL_CULL_FACE)

        # set the max level of mipmaps
        max_mip_levels = 5

        # iterate through every mipmap level
        for mip in range(max_mip_levels):
            # calculate the resolution of the mipmap level
            mip_width = rm.reflection_resolution * pow(0.5, mip)
            mip_height = rm.reflection_resolution * pow(0.5, mip)

            # adapt the renderbuffer to accomodate the new resolution
            glBindRenderbuffer(GL_RENDERBUFFER, rm.reflection_depth)
            glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, int(mip_width), int(mip_height))

            # set the viewport to the dimensions of the mipmap size
            glViewport(0, 0, int(mip_width), int(mip_height))

            # calculate the attributed roughness value
            roughness = float(mip) / float(max_mip_levels - 1)
            # bind the roughness uniform
            glUniform1f(shader.uniforms["roughness"], roughness)

            # iterate through every face of the cube
            for i in range(6):
                # update the view matrix for the correct face
                glUniformMatrix4fv(shader.uniforms["view"], 1, GL_FALSE, glm.value_ptr(rm.center_cubemap_views[i]))
                # bind the correct texture target in the framebuffer
                glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, rm.reflection_map, mip)
                # clear the framebuffer texture
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                # draw the blurred reflection map
                glDrawElements(GL_TRIANGLES, rm.indices_count["default"], GL_UNSIGNED_INT, None)

        # re-enable backface culling
        glEnable(GL_CULL_FACE)
        # set the viewport back to the renderer dimensions
        glViewport(0, 0, rm.width, rm.height)

    # ---------------------------- Link methods ----------------------------
    # method to link static uniforms to the shader (static meaning they don't change between meshes)
    def _link_shader_uniforms(self, shader):
        # get a reference to the renderer manager
        rm = RendererManager()

        if "view" in shader.uniforms:
            glUniformMatrix4fv(shader.uniforms["view"], 1, GL_FALSE, rm.camera.get_ogl_matrix())
        if "projection" in shader.uniforms:
            glUniformMatrix4fv(shader.uniforms["projection"], 1, GL_FALSE, rm.get_ogl_projection_matrix())
        if "light" in shader.uniforms:
            glUniform3f(shader.uniforms["light"], rm.light_positions[0], rm.light_positions[1], rm.light_positions[2])
        if "eye" in shader.uniforms:
            glUniform3f(shader.uniforms["eye"], rm.camera.position.x, rm.camera.position.y, rm.camera.position.z)

        if "skybox_view" in shader.uniforms:
            glUniformMatrix4fv(shader.uniforms["skybox_view"], 1, GL_FALSE, rm.camera.get_skybox_ogl_matrix())

        light_material = rm.light_material()

        if "light_ambient" in shader.uniforms:
            glUniform3f(shader.uniforms["light_ambient"], light_material.ambient[0], light_material.ambient[1], light_material.ambient[2])
        if "light_diffuse" in shader.uniforms:
            glUniform3f(shader.uniforms["light_diffuse"], light_material.diffuse[0], light_material.diffuse[1], light_material.diffuse[2])
        if "light_specular" in shader.uniforms:
            glUniform3f(shader.uniforms["light_specular"], light_material.specular[0], light_material.specular[1], light_material.specular[2])
        if "light_color" in shader.uniforms:
            glUniform3f(shader.uniforms["light_color"], light_material.diffuse[0], light_material.diffuse[1], light_material.diffuse[2])
        if "light_strength" in shader.uniforms:
            glUniform1f(shader.uniforms["light_strength"], rm.light_strengths[0])

        if "lights" in shader.uniforms:
            glUniform3fv(shader.uniforms["lights"], rm.lights_count, rm.light_positions)
        
        if "light_colors" in shader.uniforms:
            glUniform3fv(shader.uniforms["light_colors"], rm.lights_count, rm.light_colors)
        
        if "light_strengths" in shader.uniforms:
            glUniform1fv(shader.uniforms["light_strengths"], rm.lights_count, rm.light_strengths)

        if "lights_count" in shader.uniforms:
            glUniform1f(shader.uniforms["lights_count"], rm.lights_count)

        if "screen_texture" in shader.uniforms:
            glUniform1i(shader.uniforms["screen_texture"], 0)
        if "blurred_texture" in shader.uniforms:
            glUniform1i(shader.uniforms["blurred_texture"], 1)
        if "depth_texture" in shader.uniforms:
            glUniform1i(shader.uniforms["depth_texture"], 2)

        if "depth_map" in shader.uniforms:
            glUniform1i(shader.uniforms["depth_map"], 3)
        if "irradiance_map" in shader.uniforms:
            glUniform1i(shader.uniforms["irradiance_map"], 4)
        if "reflection_map" in shader.uniforms:
            glUniform1i(shader.uniforms["reflection_map"], 5)
        if "brdf_integration" in shader.uniforms:
            glUniform1i(shader.uniforms["brdf_integration"], 6)


        if "samples" in shader.uniforms:
            glUniform1i(shader.uniforms["samples"], rm.samples)

        if "cube_matrices" in shader.uniforms:
            shadow_matrices = rm.get_ogl_shadow_matrices()
            for i in range(6):
                glUniformMatrix4fv(shader.uniforms["cube_matrices"] + i, 1, GL_FALSE, shadow_matrices[i])

        if "far_plane" in shader.uniforms:
            glUniform1f(shader.uniforms["far_plane"], rm.shadow_far_plane)
        # if "cube_matrices" in shader.uniforms:
        #     glUniformMatrix4fv(shader.uniforms["cube_matrices[0]"], rm.)

    # method to link dynamic uniforms to the shader (dynamic meaning they change between meshes)
    def _link_model_uniforms(self, shader, name):
        rm = RendererManager()

        if "model" in shader.uniforms:
            glUniformMatrix4fv(shader.uniforms["model"], 1, GL_FALSE, rm.get_ogl_matrix(name))
        
    def _link_material_uniforms(self, shader, name):
        rm = RendererManager()
        model = rm.models[name]

        if "ambient" in shader.uniforms:
            glUniform3f(shader.uniforms["ambient"], rm.materials[model.material].ambient[0], rm.materials[model.material].ambient[1], rm.materials[model.material].ambient[2])
        if "diffuse" in shader.uniforms:
            glUniform3f(shader.uniforms["diffuse"], rm.materials[model.material].diffuse[0], rm.materials[model.material].diffuse[1], rm.materials[model.material].diffuse[2])
        if "specular" in shader.uniforms:
            glUniform3f(shader.uniforms["specular"], rm.materials[model.material].specular[0], rm.materials[model.material].specular[1], rm.materials[model.material].specular[2])
        if "shininess" in shader.uniforms:
            glUniform1f(shader.uniforms["shininess"], rm.materials[model.material].shininess)
        if "albedo" in shader.uniforms:
            glUniform3f(shader.uniforms["albedo"], rm.materials[model.material].diffuse[0], rm.materials[model.material].diffuse[1], rm.materials[model.material].diffuse[2])
        if "roughness" in shader.uniforms:
            glUniform1f(shader.uniforms["roughness"], rm.materials[model.material].roughness)
        if "metallic" in shader.uniforms:
            glUniform1f(shader.uniforms["metallic"], rm.materials[model.material].metallic)
        

    def _link_post_processing_uniforms(self, shader):
        if "time" in shader.uniforms:
            glUniform1f(shader.uniforms["time"], glfw.get_time() * 10)

    def _link_user_uniforms(self, shader):
        if "user_distance" in shader.uniforms:
            glUniform1f(shader.uniforms["user_distance"], shader.user_uniforms["user_distance"])
        if "user_range" in shader.uniforms:
            glUniform1f(shader.uniforms["user_range"], shader.user_uniforms["user_range"])
        if "user_parameter_0" in shader.uniforms:
            glUniform1f(shader.uniforms["user_parameter_0"], shader.user_uniforms["user_parameter_0"])
        if "user_parameter_1" in shader.uniforms:
            glUniform1f(shader.uniforms["user_parameter_1"], shader.user_uniforms["user_parameter_1"])
        if "user_parameter_2" in shader.uniforms:
            glUniform1f(shader.uniforms["user_parameter_2"], shader.user_uniforms["user_parameter_2"])
        if "user_parameter_3" in shader.uniforms:
            glUniform1f(shader.uniforms["user_parameter_3"], shader.user_uniforms["user_parameter_3"])