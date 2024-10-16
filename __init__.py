bl_info = {
    "name": "Naked Keyframe Nudge",
    "blender": (4, 00, 0),
    "category": "Animation",
    "support":"COMMUNITY",
    "description": "Keyframe Nudge without the 3d View UI",
    "location": "Dopesheet > Sidebar > My Addon",
}

import bpy

# def install_and_import(package):
#     import importlib
#     try:
#         importlib.import_module(package)
#     except ImportError:
#         import pip
#         pip.main(['install', package])
#     finally:
#         globals()[package] = importlib.import_module(package)
#
#
# install_and_import('pywin32')
from .imports import *
from .UI import *
from .KFN_Scripts.Grease.Grease_HoldFor import GP_HoldFor_Operator
from .KFN_Scripts.Grease.Grease_SpreadTo import GP_SpreadTo_Operator
from .KFN_Scripts.Grease.Grease_Nudge import GP_NudgeRight_Operator,GP_NudgeLeft_Operator

class KFNGroup(bpy.types.PropertyGroup):
    input: bpy.props.IntProperty(name="KFN input",default=2, min=1)
    affect_ns: bpy.props.BoolProperty(name="KFN affect non selected",default=True)
    affect_obj: bpy.props.BoolProperty(name="KFN affect object keys",default=True)
    affect_all_obj: bpy.props.BoolProperty(name="KFN affect all objects",default=True)


def register():
    set_console_colors()
    bpy.utils.register_class(KFNGroup)
    bpy.types.Scene.KFN = bpy.props.PointerProperty(type=KFNGroup)
    bpy.utils.register_class(GP_HoldFor_Operator)
    bpy.utils.register_class(GP_SpreadTo_Operator)
    bpy.utils.register_class(GP_NudgeLeft_Operator)
    bpy.utils.register_class(GP_NudgeRight_Operator)
    bpy.utils.register_class(PT_NakedKFNPanel)
    print(f"Blender Addon Naked Keyframe Nudge Registered")
    pass
def unregister():
    pass

if __name__ == "__main__":
    register()
