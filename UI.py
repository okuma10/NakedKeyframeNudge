import bpy

class PT_NakedKFNPanel(bpy.types.Panel):
    bl_label= "Naked Keyframe Nudge Panel"
    bl_idname= "DOPESHEET_PT_NakedKFNPanel"
    bl_space_type= "DOPESHEET_EDITOR"
    bl_region_type= "UI"

    def draw(self,context):
        layout = self.layout

        layout.label(text="NakedKFN")

        row = layout.row()
        rol_col = row.column(align=True)
        rol_col.scale_y = 2
        rol_col.prop(context.scene.KFN, "input",text="")
        rol_col.prop(context.scene.KFN, "affect_ns",text="Affect Non Selected")
        rol_col.prop(context.scene.KFN, "affect_obj",text="Affect Object Keys")
        rol_col.prop(context.scene.KFN, "affect_all_obj",text="Affect All Objects")
