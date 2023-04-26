bl_info = {
    "name": "Mecha Bevel",
    "author": "Stas Zvyagintsev",
    "version": (1, 0),
    "blender": (3, 4, 1),
    "location": "N-Panel > Mecha Bevel",
    "description": "Сreates a bevel shader",
    "warning": "",
    "doc_url": "",
    "category": "Material"
}

import bpy

from bpy.types import Operator, Panel, PropertyGroup
from bpy.utils import register_class, unregister_class


def bevel_shader_thickness(self, context):
    scene = context.scene
    mytool = scene.my_tool
    bpy.data.materials[bpy.context.object.active_material.name].node_tree.nodes["Math"].inputs[
        0].default_value = mytool.bevel_shader_thickness_property


def bevel_shader_weight(self, context):
    scene = context.scene
    mytool = scene.my_tool

    bpy.ops.paint.vertex_paint_toggle()
    bpy.context.object.data.use_paint_mask_vertex = True
    bpy.data.brushes["Draw"].color = (
        mytool.bevel_shader_weight_property, mytool.bevel_shader_weight_property, mytool.bevel_shader_weight_property)
    bpy.ops.paint.vertex_color_set()
    bpy.ops.object.editmode_toggle()


class BsPropertyes(PropertyGroup):
    bevel_shader_thickness_property: bpy.props.FloatProperty(name="Bevel Thicness", default=0, soft_min=0,
                                                             update=bevel_shader_thickness)
    bevel_shader_weight_property: bpy.props.FloatProperty(name="Bevel Shader Weight", default=1, soft_min=0, soft_max=1,
                                                          update=bevel_shader_weight)


class BS_OT_bevel_shader(Operator):
    bl_idname = "object.simple_operator"
    bl_label = "Add Bevel Material"

    def execute(self, context):
        try:
            self.viewport_render(context)
        except:
            pass

        try:
            self.set_render_parameters(context)
        except:
            pass

        scene = context.scene
        mytool = scene.my_tool

        material_basic = bpy.data.materials.new(name="Name")
        material_basic.use_nodes = True
        bpy.context.object.active_material = material_basic

        principled_node = material_basic.node_tree.nodes.get("Principled BSDF")
        principled_node.inputs[0].default_value = (0.5, 0.2, 0.2, 1)
        principled_node.inputs[6].default_value = 1
        principled_node.inputs[9].default_value = 0

        bevel_node = material_basic.node_tree.nodes.new("ShaderNodeBevel")
        bevel_node.location = (-400, -265)
        bevel_node.samples = 16
        bevel_node.inputs[0].default_value = mytool.bevel_shader_thickness_property

        try:
            mix = material_basic.node_tree.nodes.new("ShaderNodeMix")
            mix_inputs = 3
        except:
            mix = material_basic.node_tree.nodes.new("ShaderNodeMixRGB")
            mix_inputs = 2
            mix.inputs[1].default_value = (0, 0, 0, 1)

        mix.location = (-600, -320)

        mt = material_basic.node_tree.nodes.new("ShaderNodeMath")
        mt.location = (-800, -445)
        bpy.data.materials[bpy.context.object.active_material.name].node_tree.nodes[mt.name].operation = "ABSOLUTE"

        atr = material_basic.node_tree.nodes.new("ShaderNodeAttribute")
        atr.location = (-1000, -400)
        bpy.data.materials[bpy.context.object.active_material.name].node_tree.nodes[atr.name].attribute_name = "Col"

        img_tex = material_basic.node_tree.nodes.new("ShaderNodeTexImage")
        img_tex.location = (-700, -20)

        normal = material_basic.node_tree.nodes.new("ShaderNodeNormalMap")
        normal.location = (-405, 80)

        link = material_basic.node_tree.links.new

        link(bevel_node.outputs["Normal"], principled_node.inputs[22])
        link(img_tex.outputs[0], normal.inputs[1])

        link(mix.outputs[0], bevel_node.inputs[0])
        link(mt.outputs[0], mix.inputs[mix_inputs])
        link(atr.outputs[0], mix.inputs[0])

        bpy.ops.paint.vertex_paint_toggle()
        bpy.ops.paint.vertex_paint_toggle()

        return {'FINISHED'}

    def viewport_render(self, context):
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.space_data.shading.type = 'RENDERED'
        bpy.context.space_data.shading.use_scene_world_render = False
        bpy.context.space_data.shading.use_scene_lights_render = False
        bpy.context.space_data.shading.studio_light = 'forest.exr'

    def set_render_parameters(self, context):
        bpy.context.scene.cycles.preview_samples = 16
        bpy.context.scene.cycles.samples = 16
        bpy.context.scene.cycles.bake_type = 'NORMAL'
        bpy.context.scene.render.bake.margin = 0


class BS_PT_bevel_shader(Panel):
    bl_label = "Mecha Bevel Shader"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mecha Bevel"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        row = layout.row()

        if bpy.context.object.type == "MESH":
            row.operator('object.simple_operator', icon='SHADING_RENDERED')
            row = layout.row()
            layout.prop(mytool, "bevel_shader_thickness_property")
        else:
            row.label(text=f'select mesh', icon='EDITMODE_HLT')

        if bpy.context.mode == 'EDIT_MESH':
            row = layout.row()
            layout.prop(mytool, "bevel_shader_weight_property")


classes = (
    BsPropertyes,
    BS_OT_bevel_shader,
    BS_PT_bevel_shader
)


def register():
    for cl in classes:
        register_class(cl)
        bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=BsPropertyes)


def unregister():
    for cl in reversed(classes):
        unregister_class(cl)
        del bpy.types.Scene.my_tool


if __name__ == "__main__":
    register()
