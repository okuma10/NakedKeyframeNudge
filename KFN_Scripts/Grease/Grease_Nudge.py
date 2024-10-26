import bpy
import numpy as np
import types
# from ..Keyframe.Tools import *

# print(f"\033[2J")

def b_search_i(arr: list[int], target:int)->int:
    left,right=0,len(arr)-1

    while left <= right:
        mid = (left+right)>>1
        if arr[mid] == target:
            return mid
        
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


def get_mesh_keyframe_numbers(mesh_obj) -> list:
    out_data = []
    action = mesh_obj.animation_data.action
    for fcurve in action.fcurves:
        for keyframe in fcurve.keyframe_points:
            out_data.append(keyframe.co.x)
    out_data = sorted(list(set(out_data)))
    return out_data


object_types_procedure = {
    'MESH'      : get_mesh_keyframe_numbers,
    'CURVE'     : 'Curve object, TODO.',
    'SURFACE'   : 'Surface object, TODO',
    'META'      : 'Metaball object, TODO.',
    'FONT'      : 'Text object, TODO.',
    'ARMATURE'  : get_mesh_keyframe_numbers,
    'LATTICE'   : 'Lattice object, TODO.',
    'EMPTY'     : get_mesh_keyframe_numbers,
    'GPENCIL'   : get_mesh_keyframe_numbers,
    'CAMERA'    : get_mesh_keyframe_numbers,
    'LIGHT'     : 'Light object, TODO.',
    'SPEAKER'   : 'Speaker object, TODO',
    'LIGHT_PROBE': 'Light probe object, TODO.'
}

def get_list_of_animated_objects() -> list:
    animated_objects = []
    
    for object in bpy.data.objects :
        if object.animation_data:
            if object.animation_data.action:
                animated_objects.append(object.as_pointer())


    return animated_objects 

def get_keyframeNumbers_from_object_list(object_list) ->list:
    keyframe_numbers = []
    bpy_data = bpy.data.objects
    for object in bpy_data:
        if object.as_pointer() in object_list:
            current_object_keyframes = []
            if isinstance(object_types_procedure[object.type], types.FunctionType): 
                current_object_keyframes = object_types_procedure[object.type](object)
            elif isinstance(object_types_procedure[object.type], str):
                print(f"{object_types_procedure[object.type]}")
            keyframe_numbers.extend(current_object_keyframes)

    return sorted(list(set(keyframe_numbers)))


def gp_Nudge(control, affect_non_selected, affect_obj_keyframes, affect_all_objects):
    print("\033[2J")

    Pencils = [pencil for pencil in bpy.data.grease_pencils_v3 if bpy.context.active_object.data.as_pointer() == pencil.as_pointer()]
    print(f"{Pencils}")
    gp_Nudge_map = {}

    selected_keyframes = []

    # return 0 
    #n Loop through GP objects
    for pencil in Pencils:
        name = pencil.name
        layers = pencil.layers

        gp_Nudge_map[name] = [[],[]]

        #n Loop through GP object's layers
        for layer in layers:
            layer_name = layer.name
            keyframes = layer.frames

            #n Loop through GP object's keyframes for every layer
            #   populate GP map
            for keyframe in keyframes:
                keyf_frame = keyframe.frame_number
                if keyframe.select:
                    gp_Nudge_map[name][0].append(keyf_frame)
                    selected_keyframes.append(keyf_frame)
                else:
                    gp_Nudge_map[name][1].append(keyf_frame)
    
    for pencil in Pencils:
        selected_kf_x       = sorted(list(set(gp_Nudge_map[pencil.name][0]))) 
        non_selected_kf_x   = sorted(list(set(gp_Nudge_map[pencil.name][1])))
        
        # print(f"selected {selected_kf_x}\n\t  non selected {non_selected_kf_x}")
        
        new_selected_kf_x = []
        new_non_selected_kf_x = []
        
        start_position = -1
        if len(selected_kf_x) < 1 and affect_non_selected:
            start_position = bpy.context.scene.frame_current
            non_selected_kf_x = list(filter(lambda x: x >= start_position, non_selected_kf_x))
            new_non_selected_kf_x = np.array(non_selected_kf_x) + control 
        else:
            start_position      = selected_kf_x[0]
            new_selected_kf_x   = np.array(selected_kf_x) + control
            non_selected_kf_x   = list(filter(lambda x: x >= start_position, non_selected_kf_x))
            if not affect_non_selected:
                if new_selected_kf_x[-1] >= non_selected_kf_x[0]:
                    print("ERROR: Please review case where there is not enough space for Last selected")
                    return 
            else:
                new_non_selected_kf_x = np.array(non_selected_kf_x) + control 
        

        # ── Object Keyframes case ─────────────────────────────────────────────
        if affect_obj_keyframes:
            animated_objects = get_list_of_animated_objects()
            obj_keyframes = []
            if not affect_all_objects:
                # print("AAAAA")
                for obj in bpy.data.objects:
                    if obj.as_pointer() in animated_objects and not obj.data.as_pointer() == pencil.as_pointer(): 
                        animated_objects.delete(obj.as_pointer())
            obj_keyframes = get_keyframeNumbers_from_object_list(animated_objects)
            obj_keyframes = list(filter(lambda x: x >= start_position, obj_keyframes))
            new_obj_keyframes = np.array(obj_keyframes) + control
            # print(f"{ new_obj_keyframes }")

            for obj in bpy.data.objects:
                if obj.as_pointer() in animated_objects:
                    for fcurve in obj.animation_data.action.fcurves:
                        for keyframe in fcurve.keyframe_points:
                            # if keyframe.co.x in obj_keyframes:
                            try:
                                keyframe_idx = obj_keyframes.index(keyframe.co.x)
                            except ValueError:
                                continue
                            # print(f"{keyframe.co.x} keyframe_idx {keyframe_idx}")
                            keyframe.co.x = new_obj_keyframes[keyframe_idx]

        # ── Grease Pencil keyframes ───────────────────────────────────────────
        for layer in pencil.layers:
            print(f"{layer.name}")
            if not layer.lock:
                layer_keyframes = [keyframe.frame_number for keyframe in layer.frames]
                print(f"layer frames no. {len(layer_keyframes)}")
                # print(f"{selected_keyframes}")
                # print(f"{layer_keyframes}")
                
                # idx = b_search_i(selected_kf_x, layer_keyframes[i])

                print(f"\tControl {control}")
                if control > 0 :
                    
                    # ───────────────────────────── Non Selected ─────────────────────────────
                    if affect_non_selected:
                        non_sel_len = len(non_selected_kf_x)
                        for i in range(1, len(non_selected_kf_x)+1):
                            idx = non_sel_len-i
                            print(f"idx ({idx})")
                            if b_search_i(layer_keyframes, non_selected_kf_x[idx]) < 0: 
                                continue
                            print(f"{non_selected_kf_x[idx]}")
                            layer.frames.move(non_selected_kf_x[idx], new_non_selected_kf_x[idx])
                    # ─────────────────────────────── selected ───────────────────────────────
                    sel_len = len(selected_kf_x)
                    for i in range(1, len(selected_kf_x)+1):
                        idx = sel_len-i
                        if b_search_i(layer_keyframes, selected_kf_x[idx]) < 0: 
                            continue
                        print(f"{selected_kf_x[idx]}")
                        layer.frames.move(selected_kf_x[idx], new_selected_kf_x[idx])
                    print("\tLet's move those frames -->")
                    pass
                else:
                    # ─────────────────────────────── selected ───────────────────────────────
                    for i in range(len(selected_kf_x)):
                        if b_search_i(layer_keyframes, selected_kf_x[i]) < 0: 
                            continue

                        layer.frames.move(selected_kf_x[i],new_selected_kf_x[i])
                    print("\t<-- Let's move those frames")

                    # ───────────────────────────── Non Selected ─────────────────────────────
                    if affect_non_selected:
                        for i in range(len(non_selected_kf_x)):
                            if b_search_i(layer_keyframes, non_selected_kf_x[i]) < 0: 
                                continue
                            layer.frames.move(non_selected_kf_x[i], new_non_selected_kf_x[i])

                layer.frames.update()
                for frame in layer.frames:
                    if frame.frame_number in new_selected_kf_x:
                        frame.select = True

                # for keyframe in layer.frames:
                #     print(f"{keyframe.frame_number}")
                #     if len(selected_keyframes) > 0 and keyframe.frame_number in selected_kf_x:
                #         keyframe_idx = selected_kf_x.index(keyframe.frame_number)
                #         keyframe.frame_number = new_selected_kf_x[keyframe_idx]
                #         continue
                #
                #     if affect_non_selected and len(non_selected_kf_x) > 0 and keyframe.frame_number in non_selected_kf_x:
                #         keyframe_idx = non_selected_kf_x.index(keyframe.frame_number)
                #         keyframe.frame_number = new_non_selected_kf_x[keyframe_idx]

    print("Inside Nudge 23")
    return 0


# gp_Nudge(-1,1,0,0)

class GP_NudgeRight_Operator(bpy.types.Operator):
    bl_idname = "scene.kfn_gp_nudge_right"
    bl_label = "GP Nudge >"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        gp_Nudge(context.scene.KFN.input, context.scene.KFN.affect_ns, context.scene.KFN.affect_obj, context.scene.KFN.affect_all_obj)
        print(f"Executing Nudge right {context.scene.KFN.input}")
        return {'FINISHED'}


class GP_NudgeLeft_Operator(bpy.types.Operator):
    bl_idname = "scene.kfn_gp_nudge_left"
    bl_label = "GP Nudge <"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        gp_Nudge(-context.scene.KFN.input, context.scene.KFN.affect_ns, context.scene.KFN.affect_obj, context.scene.KFN.affect_all_obj)
        print(f"Executing Nudge left {context.scene.KFN.input}")
        return {'FINISHED'}  

