import bpy
import re

def get_prop_name(data_path):
    # Extracts clean property name:
    # 'pose.bones["Hand"].location' -> 'location'
    # 'pose.bones["Hand"]["IK_FK"]' -> 'IK_FK'
    if data_path.endswith('"]'):
        return data_path.rsplit('["', 1)[-1][:-2]
    return data_path.rsplit(".", 1)[-1]

def is_transform_prop(data_path, prop):
    # Custom properties use bracket notation: e.g. pose.bones["Bone"]["prop"]
    if data_path.endswith('"]'):
        return False
    return prop in {
        "location",
        "rotation_euler",
        "rotation_quaternion",
        "rotation_axis_angle",
        "scale",
        "bbone_curveinx",
        "bbone_curveiny",
        "bbone_curveoutx",
        "bbone_curveouty",
        "bbone_rollin",
        "bbone_rollout",
        "bbone_scalein",
        "bbone_scaleout",
        "bbone_easein",
        "bbone_easeout",
    }

def curve_sort_key(curve, order_mode):
    prop = get_prop_name(curve.data_path)
    is_trans = 0 if is_transform_prop(curve.data_path, prop) else 1

    if order_mode == "TRS":
        trs_order = {
            "location": 10,
            "rotation_euler": 20,
            "rotation_quaternion": 21,
            "rotation_axis_angle": 22,
            "scale": 30,
        }
        return (is_trans, trs_order.get(prop, 100), prop.casefold(), curve.array_index)
    elif order_mode == "AXIS":
        return (is_trans, curve.array_index, prop.casefold())
    elif order_mode == "ALPHA":
        return (is_trans, prop.casefold(), curve.array_index)
    return 0

def readd_curve(action, grp_ref, channel_order="NONE"):
    curves = list(grp_ref.channels)
    if channel_order != "NONE":
        curves.sort(key=lambda c: curve_sort_key(c, channel_order))
    name = grp_ref.name
    groups = get_channelbag(action).groups
    groups.remove(grp_ref)
    newgrp = groups.new(name)
    for curve in curves:
        curve.group = newgrp

def get_target_actions(self, context):
    if context.scene.use_selected:
        if not check_active_action(self):
            return None
        return [context.active_object.animation_data.action]
    return list(bpy.data.actions)

def get_channelbag(action):
    return action.layers[0].strips[0].channelbag(action.slots[0])

def check_active_action(self):
    if bpy.context.active_object == None:
        self.report({"ERROR"}, "There is no active object!") 
        return False
    if bpy.context.active_object.animation_data == None or bpy.context.active_object.animation_data.action == None :
        self.report({"ERROR"}, "Active object has no action assigned, please assign one") 
        return False
    if len(bpy.context.active_object.animation_data.action.slots) == 0:
        self.report({"ERROR"}, "Active action has no slots assigned, please assign one") 
        return False
    else:
        return True

def check_action_has_groups(self, action):
    if len(action.layers) == 0:
        self.report({"ERROR"}, "Action '"+ action.name+ "' has no layers assigned and has been skipped")
        return False
    if len(action.layers[0].strips) == 0:
        self.report({"ERROR"}, "Action '"+ action.name+ "' has no strips assigned and has been skipped")
        return False
    if len(action.slots) == 0:
        self.report({"ERROR"}, "Action '"+ action.name+ "' has no slots assigned and has been skipped")
        return False
    if len(get_channelbag(action).groups) == 0:
        self.report({"ERROR"}, "Action '"+ action.name+ "' has no groups assigned and has been skipped")
        return False
    return True

class AlphabetiseAll(bpy.types.Operator):
    """Sorts curve groups in all actions by alphabetical order"""
    bl_idname = "anim.alphabetise_all"
    bl_label = "AlphabetiseAll"
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):
        channel_order = context.scene.channel_sort_order
        actions = get_target_actions(self, context)
        if actions is None:
            return {'CANCELLED'}

        for action in actions:
            if check_action_has_groups(self, action):
                group_list = [grp.name for grp in get_channelbag(action).groups]
                sorted_group_list = sorted(group_list, key=str.casefold)
                for grp in sorted_group_list:
                    grp_ref = get_channelbag(action).groups[grp]
                    readd_curve(action, grp_ref, channel_order)

        return {'FINISHED'}

class SortbyRigHierarchy(bpy.types.Operator):
    """Sorts curve groups in all actions by their order in the rig hierarchy"""
    bl_idname = "anim.sort_by_rig"
    bl_label = "SortbyRigHierarchy"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        channel_order = context.scene.channel_sort_order
        root_bones = []
        ordered_bones = []

        if bpy.context.active_object == None:
            self.report({"ERROR"}, "There is no active object!") 
            return {'CANCELLED'}
        if bpy.context.active_object.type != "ARMATURE":
            self.report({'ERROR'}, "Active object is not an armature! Please select the armature you want to sort by")
            return {'CANCELLED'}
        for bone in bpy.context.active_object.pose.bones:
            if bone.parent == None:
                root_bones.append(bone)
                ordered_bones.append(bone.name)

        for bone in root_bones:
            path_finished = False
            current_bone = bone
                
            while path_finished == False:
                valid_child_found = False
                for child in current_bone.children:
                    if child.name not in ordered_bones:
                        ordered_bones.append(child.name)                
                    if len(child.children)>0:
                        if child.children[0].name not in ordered_bones:
                            current_bone = child
                            valid_child_found = True
                            break
                
                if valid_child_found == False:
                    if current_bone.parent == None:
                        path_finished = True
                        break
                    else:
                        current_bone = current_bone.parent

        actions = get_target_actions(self, context)
        if actions is None:
            return {'CANCELLED'}

        for action in actions:
            if check_action_has_groups(self, action):
                cbag = get_channelbag(action)
                non_rig_groups = [g for g in cbag.groups if g.name not in ordered_bones]
                for bone_name in ordered_bones:
                    if bone_name in cbag.groups:
                        readd_curve(action, cbag.groups[bone_name], channel_order)
                for group in non_rig_groups:
                    readd_curve(action, group, channel_order)

        return {'FINISHED'}

class GroupOrphanedCurves(bpy.types.Operator):
    """Takes orphaned bone curves and puts them in a group"""
    bl_idname = "anim.group_orphaned_curves"
    bl_label = "GroupOrphanedCurves"
    bl_options = {"REGISTER", 'UNDO'}

    def execute(self, context):
        actions = get_target_actions(self, context)
        if actions is None:
            return {'CANCELLED'}

        for action in actions:
            if check_action_has_groups(self, action) == True:
                for fcurve in get_channelbag(action).fcurves:
                    if fcurve.group == None:
                        if "pose.bones" in fcurve.data_path:
                            #parse datapath for bonename
                            bonename = re.findall(r'pose\.bones\["(.*?)"\]', fcurve.data_path)
                            if not bonename:
                                continue
                            bonename = bonename[0]
                            cbag = get_channelbag(action)
                            try:
                                fcurve.group = cbag.groups[bonename] #if it already exists, re-add it
                            except:
                                cbag.groups.new(bonename) #otherwise make a new one
                                fcurve.group = cbag.groups[bonename]

        return {'FINISHED'}


class GroupCustomProperties(bpy.types.Operator):
    """Groups custom properties curves that don't belong to a bone under their own group """
    bl_idname = "anim.group_custom_properties"
    bl_label = "GroupCustomProperties"
    bl_options = {"REGISTER", 'UNDO'}

    def execute(self, context):
        actions = get_target_actions(self, context)
        if actions is None:
            return {'CANCELLED'}

        for action in actions:
            if check_action_has_groups(self, action) == True:
                cbag = get_channelbag(action)
                for fcurve in cbag.fcurves:
                    if fcurve.group == None:
                        if "pose.bones" not in fcurve.data_path:
                            try:
                                fcurve.group = cbag.groups["Custom Properties"]
                            except:
                                cbag.groups.new("Custom Properties")
                                fcurve.group = cbag.groups["Custom Properties"]

        return {'FINISHED'}

class CopyGroupstoAll(bpy.types.Operator):
    """Copies the curve group layout from the master action to all actions"""
    bl_idname = "anim.copy_groups_to_all"
    bl_label = "CopyGroupstoAll"
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):
        channel_order = context.scene.channel_sort_order
        master_groups = []
        try:
            master_action = bpy.data.actions[bpy.context.scene.master_action]
        except:
            self.report({'ERROR'}, "No action assigned to copy groups from!")
            return {'CANCELLED'}
            
        if check_action_has_groups(self, master_action) == True:
            for grp in master_action.layers[0].strips[0].channelbag(master_action.slots[0]).groups:
                master_groups.append(grp.name)
        else:
            self.report({'ERROR'}, "Master action is invalid, copy cancelled!")
            return {'CANCELLED'}            
            
        missing_actions_groups_dict = {}
        unreferenced_actions_groups_dict = {}
        actions = get_target_actions(self, context)
        if actions is None:
            return {'CANCELLED'}

        for action in actions:
            if check_action_has_groups(self, action):
                if action == master_action:
                    continue
                cbag = get_channelbag(action)
                unreferenced_groups = [grp for grp in cbag.groups if grp.name not in master_groups]
                if unreferenced_groups:
                    unreferenced_actions_groups_dict[action.name] = [g.name for g in unreferenced_groups]

                for grp_name in master_groups:
                    if grp_name in cbag.groups:
                        readd_curve(action, cbag.groups[grp_name], channel_order)
                    else:
                        missing_actions_groups_dict.setdefault(action.name, []).append(grp_name)

                for grp_ref in unreferenced_groups:
                    readd_curve(action, grp_ref, channel_order)               

         
        print("\n ----- Actions missing groups from the master action: -----")           
        for key in missing_actions_groups_dict.keys():
            print("\n Action:", key)
            for group in missing_actions_groups_dict[key]:
                print("       - '"+group+"'")

        print("\n ----- Actions with groups that don't appear in the master action (added to bottom of the group stack) : -----")    
        for key in unreferenced_actions_groups_dict.keys():
            print("\n Action:", key)
            for group in unreferenced_actions_groups_dict[key]:
                print("       - '"+group+"'")

        return {'FINISHED'}



class SortChannelsOnly(bpy.types.Operator):
    """Sorts channels within groups without changing group order"""
    bl_idname = "anim.sort_channels_only"
    bl_label = "Sort Channels Only"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        channel_order = context.scene.channel_sort_order
        if channel_order == "NONE":
            self.report({'INFO'}, "Channel sort order is set to None")
            return {'CANCELLED'}

        actions = get_target_actions(self, context)
        if actions is None:
            return {'CANCELLED'}

        for action in actions:
            if check_action_has_groups(self, action):
                cbag = get_channelbag(action)
                for grp in list(cbag.groups):
                    readd_curve(action, grp, channel_order)

        return {'FINISHED'}

CLASSES =  [AlphabetiseAll, CopyGroupstoAll, SortbyRigHierarchy, GroupCustomProperties, GroupOrphanedCurves, SortChannelsOnly]

def register_operators():
    for klass in CLASSES:
        bpy.utils.register_class(klass)

def unregister_operators():
    for klass in CLASSES:
        bpy.utils.unregister_class(klass)



if __name__ == '__main__':
    register_operators()
                        
