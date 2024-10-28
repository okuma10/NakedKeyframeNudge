import bpy
import numpy as np
import types
# import bisect
# from ..Tools import b_search_i

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

print("\033[2J")
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

    return keyframe_numbers


def Hold_For(usr_inp, affect_non_selected, affect_object_keys, affect_all_objects):
    #n <-- initial data from Belnder -->
    control = usr_inp
    pencils = [pencil for pencil in bpy.data.grease_pencils_v3 if pencil.as_pointer() == bpy.context.active_object.data.as_pointer() ] #?
    #n <-- global variable declaration -->
    gp_HoldFor_map = {}

    selected_keyframes = []
    layers_with_selectedKf = []
    objects_with_selectedKf = []
    
    # affect_object_keys = True
    affect_other_grease_pencils = True
    # affect_all_objects = True

    #n <--  Initial data collection -->
    for pencil in pencils:
        name = pencil.name
        gp_HoldFor_map[name] = [[], []]
        layers = pencil.layers

        for layer in layers:
            layer_name = layer.name
            keyframes_selected = [keyframe.frame_number for keyframe in layer.frames if keyframe.select]

            if len(keyframes_selected):
                keyframes_non_selected = [keyframe.frame_number for keyframe in layer.frames if
                                          not keyframe.select and keyframe.frame_number > keyframes_selected[-1]]

                for keyframe in keyframes_selected:
                    gp_HoldFor_map[name][0].append(keyframe)
                    selected_keyframes.append(keyframe)

                for keyframe in keyframes_non_selected:
                    gp_HoldFor_map[name][1].append(keyframe)

            # Mark layers with selected keyframes
            if len(selected_keyframes) > 0:
                layers_with_selectedKf.append(layer_name)
            selected_keyframes.clear()

        # Modify Map - populate object moding list if object has a layer with selected keyframes
        if len(layers_with_selectedKf) > 0:
            objects_with_selectedKf.append(name)
        layers_with_selectedKf.clear()


    # Remove Pencils with 0 selected keyframes.
    if len(objects_with_selectedKf) > 0:
        non_active_pencils = [pencil.name for pencil in pencils if pencil.name not in objects_with_selectedKf]
        for pencil in non_active_pencils:
            del gp_HoldFor_map[pencil]
    del objects_with_selectedKf
    
    #n <--  Process Data  -->
    for pencil in pencils:
        if pencil.name in gp_HoldFor_map.keys():
            if gp_HoldFor_map[pencil.name][0]:
                # Cleanup data
                clean_non_selected = [keyframe for keyframe in gp_HoldFor_map[pencil.name][1] if
                                      keyframe not in gp_HoldFor_map[pencil.name][0]]
                gp_HoldFor_map[pencil.name][1] = clean_non_selected

                selected_kf_x     = np.array(sorted(list(set(gp_HoldFor_map[pencil.name][0]))))
                non_selected_kf_x = np.array(sorted(list(set(gp_HoldFor_map[pencil.name][1]))))
                # Create new position for selected keyframes for based on user input
                new_selected_kf_x = []
                new_non_selected_kf_x = []
                start_frame = selected_kf_x[0]
                if(affect_non_selected):
                    for i in range(len(selected_kf_x)):
                        if start_frame == selected_kf_x[0]:
                            new_selected_kf_x.append(start_frame)
                            start_frame += control
                        else:
                            new_selected_kf_x.append(start_frame)
                            start_frame += control

                    # Create new position for non selected keyframes based on new last selected position
                    if len(non_selected_kf_x):
                        distance = new_selected_kf_x[-1] - non_selected_kf_x[0] + control
                        new_non_selected_kf_x = non_selected_kf_x + distance
                else:
                    for i in range(len(selected_kf_x)):
                        if start_frame == selected_kf_x[0]:
                            new_selected_kf_x.append(start_frame)
                            start_frame += control

                        elif i == len(selected_kf_x)-1:
                            # Non Selected Control
                            non_selected =  bpy.context.scene.frame_end;
                            if len(non_selected_kf_x)>0:
                                non_selected = non_selected_kf_x[0];
                            

                            for i in range(1,len(new_selected_kf_x)+1): 
                                if i == len(new_selected_kf_x):break  

                                new_pos = new_selected_kf_x[( i * -1)] # getting the loop backwards
                                dist_to_non_selected = non_selected - new_pos
                                if dist_to_non_selected < control : 
                                    new_pos = non_selected - (i+1)
                                    new_selected_kf_x[i * -1] = new_pos
                            

                            previous_selected_new_x = new_selected_kf_x[-1]
                            last_selected_new_x = previous_selected_new_x + control
                            distance_to_non_sel = non_selected - last_selected_new_x
                            
                            last_selected_new_x = last_selected_new_x 
                            if distance_to_non_sel < control:
                                if distance_to_non_sel < 1 :
                                    last_selected_new_x = non_selected - 1
                

                            new_selected_kf_x.append(last_selected_new_x)
                        else:
                            new_selected_kf_x.append(start_frame)
                            start_frame += control
                
                # ───────────────── If we want to affect object keyframes ────────────────
                if affect_object_keys:
                    animated_objects = get_list_of_animated_objects()
                    # ──────────────────── If we want to affect only the active GP object keys ────────────────────
                    # ──────────────────────── Process animated objects ────────────────────────
                    for object in bpy.data.objects:
                        if object.as_pointer() in animated_objects: # Get the object based on the stored pointer
                            # ───── if we don't want to affect all objects then we filter only the ─────
                            #       active GP's keyframes
                            if not affect_all_objects:
                                if object.data.as_pointer() == pencil.as_pointer():
                                    continue

                            # ─────────────────────── Affect an animated object ──────────────────────
                            # __________ Filter keyframes in the selection range and past it _________
                            keyframe_numbers = get_mesh_keyframe_numbers(object)

                            obj_keyframes_in_selected_range = []
                            obj_keyframes_after_selected_range = []
                            
                            for keyframe in keyframe_numbers:
                                if selected_kf_x[0] <= keyframe :
                                    if keyframe <= selected_kf_x[-1]:
                                        obj_keyframes_in_selected_range.append(keyframe)
                                    else:
                                        obj_keyframes_after_selected_range.append(keyframe)

                            # _____________ Do not process object if both ranges are empty _____________
                            if len(obj_keyframes_in_selected_range) < 1 and len(obj_keyframes_after_selected_range)<1:
                                continue
                            
                            # ________________________ Calculate new positions _______________________
                            new_obj_keyframes_in_selected_range = []
                            new_obj_keyframes_after_selected_range = []
                            
                            # _____________________ In Selected Range calculation ____________________
                            for obj_keyframe in obj_keyframes_in_selected_range:
                                idx = np.where(selected_kf_x == obj_keyframe)[0] # find if the object keyframe is on a GP keyframe
                                if idx.size: # if it is
                                    new_obj_keyframes_in_selected_range.append(new_selected_kf_x[idx[0]])
                                    continue
                                else: # if it is not -> calculate the distance to the keyframe that is on a GP keyframe and keep that distance in the new keyframe pos list
                                    next_higher_idx         = np.searchsorted(selected_kf_x, obj_keyframe, side="right") # get the nearest to the right
                                    distance_to_next_higher = obj_keyframe - selected_kf_x[next_higher_idx]              # calculate the distance
                                    new_obj_keyframes_in_selected_range.append(new_selected_kf_x[next_higher_idx] + distance_to_next_higher)

                            # ___ If we are affecting the Non selected, Calculate the new positions __
                            if affect_non_selected and len(obj_keyframes_after_selected_range) and len(new_non_selected_kf_x):
                                selected_to_non_selected_distance       = new_non_selected_kf_x[0] - new_selected_kf_x[-1]
                                new_obj_keyframes_after_selected_range  = np.array(obj_keyframes_after_selected_range, dtype=np.int64) # Converting to Numpy array for easier modificiation
                                
                                # ____ if the sapce between the last selected and first non selected is ____
                                #       smaller calculate the space to be added so it fits the `control` requirement
                                if obj_keyframes_after_selected_range[0] - new_obj_keyframes_in_selected_range[-1] < selected_to_non_selected_distance:
                                    difference = int(selected_to_non_selected_distance - ( obj_keyframes_after_selected_range[0] - new_obj_keyframes_in_selected_range[-1] ) )
                                    new_obj_keyframes_after_selected_range +=  difference
                                # ________________________ if there is enough space ________________________
                                #   calculate the space to be removed so it fits the `control` requirement
                                else:
                                    # _______ We have to find the first keyframe that hits a GP keyframe _______
                                    #       Note: Probably a case where there is no such keyframe will require different approach
                                    obj_after_keyframe_on_gp_keyframe = -1
                                    guard = 0 # guard for infinite loop and out of bounds
                                    while obj_after_keyframe_on_gp_keyframe < 0 and guard < len(obj_keyframes_after_selected_range):
                                        for i in range(len(obj_keyframes_after_selected_range)):
                                            keyframe = obj_keyframes_after_selected_range[i]
                                            if keyframe == non_selected_kf_x[0]:
                                                obj_after_keyframe_on_gp_keyframe = keyframe
                                                break
                                            else:
                                                items_to_end = ( len(obj_keyframes_after_selected_range)-1 ) - i
                                                for j in range(1,items_to_end):
                                                    future_keyframe = obj_keyframes_after_selected_range[i+j]
                                                    if future_keyframe == non_selected_kf_x[0]:
                                                        obj_after_keyframe_on_gp_keyframe = future_keyframe
                                                        break
                                        guard +=1
                                    # print(f"{guard} - {obj_after_keyframe_on_gp_keyframe}")
                                    # ____________________ find the number to subtract with ____________________
                                    subtract_distance = int( obj_after_keyframe_on_gp_keyframe - ( new_obj_keyframes_in_selected_range[-1] + control ) )
                                    new_obj_keyframes_after_selected_range -= subtract_distance
                            # return 0
                            # ___________________ Set the newly calculated positions ___________________
                            for fcurve in object.animation_data.action.fcurves:
                                for keyframe in fcurve.keyframe_points:

                                    if keyframe.co.x in obj_keyframes_in_selected_range:
                                        idx = obj_keyframes_in_selected_range.index(keyframe.co.x)
                                        keyframe.co.x = new_obj_keyframes_in_selected_range[idx]
                                        continue

                                    elif keyframe.co.x in obj_keyframes_after_selected_range and affect_non_selected and len(obj_keyframes_after_selected_range) and len(new_obj_keyframes_after_selected_range):
                                        idx = obj_keyframes_after_selected_range.index(keyframe.co.x)
                                        keyframe.co.x = new_obj_keyframes_after_selected_range[idx]

                                    else:
                                        pass
                # return 0
                # ────────────────────────── Grease Pencil Keys ──────────────────────────
                # Assign new data to old positions
                layers = pencil.layers
                for layer in layers:
                    print(f"{layer.name}",end=" ")
                    if not layer.lock:
                        print("🔓")
                        # continue
                        keyframes = layer.frames # list of layer keyframe objects(for later use)
                        keyframe_fns = [keyframe.frame_number for keyframe in keyframes] # a list of the layer keyframe positions(used to pass if we don't have a keyframe corresponding to selected or non selected x lists)


                        m = len(selected_kf_x)
                        n = len(non_selected_kf_x)
                        # Because of new GPv3 will return ERROR on collisions we have to find the direction
                        #   of the change so we reorder opearations and loops to avoid collisions
                        direction = 0
                        if m > 1 and ( affect_non_selected or not affect_non_selected ):
                            print("Case 1")
                            direction = new_selected_kf_x[1] - selected_kf_x[1]
                            if direction == 0 and affect_non_selected:
                                direction = selected_kf_x[-1] - non_selected_kf_x[0]
                        elif affect_non_selected:
                            print("Case 2")
                            direction = new_non_selected_kf_x[0] - non_selected_kf_x[0]

                        print(f"direction {'<-' if direction < 0 else ('->' if direction > 0 else '|') } {direction}")

                        if direction < 0:
                            # Selected
                            for i in range(0, m): 
                                if(b_search_i(keyframe_fns, selected_kf_x[i]) < 0):continue
                                if selected_kf_x[i] == new_selected_kf_x[i]: continue
                                print(f" ◆ {selected_kf_x[i]} | {new_selected_kf_x[i]}")
                                layer.frames.move(selected_kf_x[i], new_selected_kf_x[i])
                            # Non Selected
                            if affect_non_selected:
                                if n > 0:
                                    for i in range(0, n): 
                                        if(b_search_i(keyframe_fns, non_selected_kf_x[i]) < 0):continue
                                        print(f" ◇ {non_selected_kf_x[i]} | {new_non_selected_kf_x[i]}")
                                        if non_selected_kf_x[i] == new_non_selected_kf_x[i]: continue
                                        layer.frames.move(non_selected_kf_x[i], new_non_selected_kf_x[i])
                        elif direction > 0:
                            # Non Selected
                            if affect_non_selected:
                                if n > 0:
                                    for i in range(1, n+1): # Reverse loop
                                        if(b_search_i(keyframe_fns, non_selected_kf_x[n-i]) < 0):continue
                                        if non_selected_kf_x[n-i] == new_non_selected_kf_x[n-i]: continue
                                        print(f" ◇ {non_selected_kf_x[n-i]} | {new_non_selected_kf_x[n-i]}")
                                        layer.frames.move(non_selected_kf_x[n-i], new_non_selected_kf_x[n-i])

                            # Selected
                            for i in range(1, m+1): # Reverse loop
                                if(b_search_i(keyframe_fns, selected_kf_x[m-i]) < 0):continue
                                if selected_kf_x[m-i] == new_selected_kf_x[m-i]: continue
                                print(f" ◆ {selected_kf_x[m-i]} | {new_selected_kf_x[m-i]}")
                                layer.frames.move(selected_kf_x[m-i], new_selected_kf_x[m-i])
                        else:
                            print(f" ERROR : You are appling the script to a single frame while not affecting the non selected keyframes.\n\t Or your distance to the next keyframe is already {control}.\nStatus: \n\taffect_non_selected{affect_non_selected}\n\taffect_object_keys{affect_object_keys}\n\taffect_all_objects{affect_all_objects}")


                        for keyframe in keyframes:
                            if keyframe.frame_number in new_selected_kf_x:
                                keyframe.select = True

                    else:
                        print("🔒")

            # if no selected keyframes , report error
            else:
                print(f'No keyframes selected for object {pencil.name}')

# Hold_For(2,1,0,0)

class GP_HoldFor_Operator(bpy.types.Operator):
    bl_idname = "scene.kfn_gp_holdfor"
    bl_label = "GP HoldFor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Hold_For(context.scene.KFN.input, context.scene.KFN.affect_ns, context.scene.KFN.affect_obj, context.scene.KFN.affect_all_obj)
        print("Executing Test Operator")
        return {'FINISHED'}  
