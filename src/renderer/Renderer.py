from utils.Singleton import Singleton
from OpenGL.GL import *
import numpy as np
import glm
import glfw

from utils.Timer import Timer
from renderer.RendererManager import RendererManager
from window.Window import Window
from renderer.instance import Instance

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
        # enable alpha blending (transparency)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # timer to keep track of the rendering time
        self.timer = Timer()

    # ---------------------------- Render methods ---------------------------
    # method to render the 3D models
    def render(self):
        # reset the timer
        self.timer.reset()

        rm = RendererManager()

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
        # render the blur texture
        self._render_blur()
        # apply depth of field effect to the main texture
        self._render_depth_of_field()
        # apply post processing effects
        self._render_post_processing()

        # draw the render quad to it
        # self._render_screen()

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
            glDrawElements(GL_TRIANGLES, int(rm.indices_count[model.mesh]), GL_UNSIGNED_INT, None)

    # method to render instanced models
    def _render_instances(self):
        # reference to the renderer manager
        rm = RendererManager()

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
        glBindVertexArray(rm.vaos["default_mesh"])
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, rm.ebos["default_mesh"])

        # disable cull facing
        glDisable(GL_CULL_FACE)
        glBindTexture(GL_TEXTURE_CUBE_MAP, rm.skybox_texture)
        glDrawElements(GL_TRIANGLES, int(rm.indices_count["default_mesh"]), GL_UNSIGNED_INT, None)
        glEnable(GL_CULL_FACE)

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
        glBindTexture(GL_TEXTURE_2D, rm.color_render_texture)
        # draw the blurred image
        glDrawElements(GL_TRIANGLES, int(rm.indices_count["screen_quad"]), GL_UNSIGNED_INT, None)

        # bind the blurred texture as source
        glBindTexture(GL_TEXTURE_2D, rm.blurred_texture)
        # for i in range(2):
        #     glDrawElements(GL_TRIANGLES, int(rm.indices_count["screen_quad"]), GL_UNSIGNED_INT, None)
        # use the dilation shader
        rm.shaders["post_processing/dilation"].use()
        # render the dilated texture
        glDrawElements(GL_TRIANGLES, int(rm.indices_count["screen_quad"]), GL_UNSIGNED_INT, None)

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
        glBindFramebuffer(GL_FRAMEBUFFER, rm.render_framebuffer)
        
        # use the depth of field shader
        rm.shaders["depth_of_field"].use()
        # link the shader specific uniforms
        self._link_shader_uniforms(rm.shaders["depth_of_field"])

        # bind the required textures to the correct texture slots
        glActiveTexture(GL_TEXTURE0 + 0)
        glBindTexture(GL_TEXTURE_2D, rm.color_render_texture)

        glActiveTexture(GL_TEXTURE0 + 1)
        glBindTexture(GL_TEXTURE_2D, rm.blurred_texture)

        glActiveTexture(GL_TEXTURE0 + 2)
        glBindTexture(GL_TEXTURE_2D, rm.depth_texture)

        # draw the scene with depth of field
        glDrawElements(GL_TRIANGLES, int(rm.indices_count["screen_quad"]), GL_UNSIGNED_INT, None)

        # set back the active texture slot to index 0
        glActiveTexture(GL_TEXTURE0)
        # re-enable depth testing
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

        # bind the render framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, rm.render_framebuffer)

        # for every effect in the post processing list
        for i in range(len(rm.post_processing_shaders)):
            # use the current post processing effect
            rm.post_processing_shaders[i].use()
            # link the post processing uniforms
            self._link_post_processing_uniforms(rm.post_processing_shaders[i])
            # link the shader specific uniforms
            self._link_shader_uniforms(rm.post_processing_shaders[i])
            # link the user specific uniforms
            self._link_user_uniforms(rm.post_processing_shaders[i])

            # bind the textures to the relative texture slots
            glActiveTexture(GL_TEXTURE0 + 0)
            glBindTexture(GL_TEXTURE_2D, rm.color_render_texture)

            glActiveTexture(GL_TEXTURE0 + 1)
            glBindTexture(GL_TEXTURE_2D, rm.blurred_texture)

            glActiveTexture(GL_TEXTURE0 + 2)
            glBindTexture(GL_TEXTURE_2D, rm.depth_texture)

            # set back the active texture slot to 0
            glActiveTexture(GL_TEXTURE0)

            # render the effect
            glDrawElements(GL_TRIANGLES, int(rm.indices_count["screen_quad"]), GL_UNSIGNED_INT, None)

        # re-enable depth testing
        glEnable(GL_DEPTH_TEST)

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
            glUniform3f(shader.uniforms["light"], rm.light_source.x, rm.light_source.y, rm.light_source.z)
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

        if "screen_texture" in shader.uniforms:
            glUniform1i(shader.uniforms["screen_texture"], 0)
        if "blurred_texture" in shader.uniforms:
            glUniform1i(shader.uniforms["blurred_texture"], 1)
        if "depth_texture" in shader.uniforms:
            glUniform1i(shader.uniforms["depth_texture"], 2)

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
       
    def _link_post_processing_uniforms(self, shader):
        if "time" in shader.uniforms:
            glUniform1f(shader.uniforms["time"], glfw.get_time() * 10)
            print(glfw.get_time())

    def _link_user_uniforms(self, shader):
        if "user_distance" in shader.uniforms:
            glUniform1f(shader.uniforms["user_distance"], shader.user_uniforms["user_distance"])
        if "user_range" in shader.uniforms:
            glUniform1f(shader.uniforms["user_range"], shader.user_uniforms["user_range"])