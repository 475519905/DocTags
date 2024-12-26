bl_info = {
    "name": "Scene Tabs Manager",
    "author": "Your Name",
    "version": (1, 3),
    "blender": (2, 80, 0),
    "location": "3D View Header",
    "description": "Manage multiple scenes like browser tabs in the 3D View header",
    "category": "Scene",
}

import bpy
from bpy.props import StringProperty

# 操作：切换场景
class SCENETABS_OT_switch_scene(bpy.types.Operator):
    bl_idname = "scene_tabs.switch_scene"
    bl_label = "Switch Scene"
    bl_description = "Switch to selected scene"
    bl_options = {'UNDO'}

    scene_name: StringProperty()

    def execute(self, context):
        if self.scene_name in bpy.data.scenes:
            context.window.scene = bpy.data.scenes[self.scene_name]
            return {'FINISHED'}
        return {'CANCELLED'}

# 操作：添加新场景
class SCENETABS_OT_add_scene(bpy.types.Operator):
    bl_idname = "scene_tabs.add_scene"
    bl_label = "Add New Scene"
    bl_description = "Add a new scene"
    bl_options = {'UNDO'}

    def execute(self, context):
        new_scene_name = "NewScene"
        index = 1
        while new_scene_name in bpy.data.scenes:
            new_scene_name = f"NewScene.{index}"
            index += 1
        new_scene = bpy.data.scenes.new(new_scene_name)
        context.window.scene = new_scene
        return {'FINISHED'}

# 操作：关闭（删除）指定场景
class SCENETABS_OT_close_scene(bpy.types.Operator):
    bl_idname = "scene_tabs.close_scene"
    bl_label = "Close Scene"
    bl_description = "Close the selected scene"
    bl_options = {'UNDO'}

    scene_name: StringProperty()

    def execute(self, context):
        scene = bpy.data.scenes.get(self.scene_name)
        if scene:
            all_scenes = list(bpy.data.scenes)
            if len(all_scenes) > 1:
                # 确保不删除当前场景
                if scene == context.scene:
                    # 切换到下一个场景
                    idx = all_scenes.index(scene)
                    new_idx = (idx + 1) % len(all_scenes)
                    context.window.scene = all_scenes[new_idx]
                bpy.data.scenes.remove(scene)
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "Cannot remove the only remaining scene.")
                return {'CANCELLED'}
        return {'CANCELLED'}

# 操作：重命名当前场景
class SCENETABS_OT_rename_scene(bpy.types.Operator):
    bl_idname = "scene_tabs.rename_scene"
    bl_label = "Rename Current Scene"
    bl_description = "Rename the currently active scene"
    bl_options = {'UNDO'}

    new_name: StringProperty(name="New Scene Name")

    def invoke(self, context, event):
        self.new_name = context.scene.name
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        if self.new_name.strip() == "":
            self.report({'WARNING'}, "Scene name cannot be empty.")
            return {'CANCELLED'}

        # 检查重名
        if self.new_name in bpy.data.scenes and bpy.data.scenes[self.new_name] != context.scene:
            self.report({'WARNING'}, "A scene with that name already exists.")
            return {'CANCELLED'}

        context.scene.name = self.new_name
        return {'FINISHED'}

# 在3D视图头部绘制场景标签
def draw_scene_tabs(self, context):
    layout = self.layout
    scene = context.scene

    # 创建一个水平行，用于放置所有按钮
    row = layout.row(align=True)

    # 添加“Scene Tabs”标签和图标
    row.label(text="Scene Tabs:", icon='SCENE_DATA')

    # 遍历所有场景，创建标签和关闭按钮
    for s in bpy.data.scenes:
        is_current = (s == scene)
        # 创建一个分割区域，用于名称和关闭按钮
        sub = row.split(factor=0.8, align=True)
        sub.operator("scene_tabs.switch_scene", text=s.name, emboss=is_current).scene_name = s.name
        # 关闭按钮
        if s.users > 0:  # 确保场景有用户，避免删除内置场景
            sub.operator("scene_tabs.close_scene", text="", icon='X', emboss=False).scene_name = s.name

    # 添加一个分隔符，将“+”按钮推到最右侧
    row.separator(factor=1.0)

    # 添加新场景按钮
    row.operator("scene_tabs.add_scene", text="", icon="ADD")

    # 重命名当前场景按钮
    row.operator("scene_tabs.rename_scene", text="", icon="FILE_TEXT")

classes = (
    SCENETABS_OT_switch_scene,
    SCENETABS_OT_add_scene,
    SCENETABS_OT_close_scene,
    SCENETABS_OT_rename_scene,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # 将自定义绘制函数预置到 3D 视图头部，以确保在最左边显示
    bpy.types.VIEW3D_HT_header.prepend(draw_scene_tabs)

def unregister():
    # 从 3D 视图头部移除
    bpy.types.VIEW3D_HT_header.remove(draw_scene_tabs)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
