import bpy
import re

def readd_curve(action, grp_ref):
    curves = []
    for curve in grp_ref.channels:
        curves.append(curve)
    name = grp_ref.name
    action.groups.remove(grp_ref)
    newgrp = action.layers[0].strips[0].channelbag(action.slots[0]).groups.new(name)
    for curve in curves:
        curve.group = newgrp

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
    if len(action.layers[0].strips[0].channelbag(action.slots[0]).groups) == 0:
        self.report({"ERROR"}, "Action '"+ action.name+ "' has no groups assigned and has been skipped") 
        return False   
    else:
        return True

class AlphabetiseAll(bpy.types.Operator):
    """Sorts curve groups in all actions by alphabetical order"""
    bl_idname = "anim.alphabetise_all"
    bl_label = "AlphabetiseAll"
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):

        if context.scene.use_selected == False:
            actions = bpy.data.actions
        else:
            if check_active_action(self) == False:
                return {'CANCELLED'}
            actions = [bpy.context.active_object.animation_data.action]

        for action in actions:
            if check_action_has_groups(self, action) == True:
                group_list = []
                for grp in action.layers[0].strips[0].channelbag(action.slots[0]).groups:
                    group_list.append(grp.name)
                sorted_group_list = sorted(group_list, key=str.casefold)
                for grp in sorted_group_list:
                    grp_ref = action.layers[0].strips[0].channelbag(action.slots[0]).groups[grp]
                    readd_curve(action, grp_ref)

        return {'FINISHED'}

class SortbyRigHierarchy(bpy.types.Operator):
    """Sorts curve groups in all actions by their order in the rig hierarchy"""
    bl_idname = "anim.sort_by_rig"
    bl_label = "SortbyRigHierarchy"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):    

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

        if bpy.context.scene.use_selected == True:
            if check_active_action(self) == False:
                return {'CANCELLED'}
            actions = [bpy.context.active_object.animation_data.action]
        else:
            actions = bpy.data.actions

        for action in actions:
            if check_action_has_groups(self, action) == True:
                non_rig_groups = []
                for group in action.layers[0].strips[0].channelbag(action.slots[0]).groups:
                    if group.name not in ordered_bones:
                        non_rig_groups.append(group)
                for bone_name in ordered_bones:
                    try:
                        grp_ref = action.layers[0].strips[0].channelbag(action.slots[0]).groups[bone_name]
                    except: 
                        continue
                    readd_curve(action,grp_ref)
                for group in non_rig_groups:
                    readd_curve(action,group)

        return {'FINISHED'}

class GroupOrphanedCurves(bpy.types.Operator):
    """Takes orphaned bone curves and puts them in a group"""
    bl_idname = "anim.group_orphaned_curves"
    bl_label = "GroupOrphanedCurves"
    bl_options = {"REGISTER", 'UNDO'}

    def execute(self, context):

        if bpy.context.scene.use_selected == True:
            if check_active_action(self) == False:
                return {'CANCELLED'}
            actions = [bpy.context.active_object.animation_data.action]
        else:
            actions = bpy.data.actions

        for action in actions:
            if check_action_has_groups(self, action) == True:
                for fcurve in action.layers[0].strips[0].channelbag(action.slots[0]).fcurves:
                    if fcurve.group == None:
                        if "pose.bones" in fcurve.data_path:
                            #parse datapath for bonename
                            bonename = re.findall('pose.bones\["(.*?)\"]', fcurve.data_path)
                            bonename = bonename[0]
                            try:
                                fcurve.group = action.layers[0].strips[0].channelbag(action.slots[0]).groups[bonename] #if it already exists, re-add it
                            except:
                                action.layers[0].strips[0].channelbag(action.slots[0]).groups.new(bonename) #otherwise make a new one
                                fcurve.group = action.layers[0].strips[0].channelbag(action.slots[0]).groups[bonename]

        return {'FINISHED'}


class GroupCustomProperties(bpy.types.Operator):
    """Groups custom properties curves that don't belong to a bone under their own group """
    bl_idname = "anim.group_custom_properties"
    bl_label = "GroupCustomProperties"
    bl_options = {"REGISTER", 'UNDO'}

    def execute(self, context):

        if bpy.context.scene.use_selected == True:
            if check_active_action(self) == False:
                return {'CANCELLED'}
            actions = [bpy.context.active_object.animation_data.action]
        else:
            actions = bpy.data.actions

        for action in actions:
            if check_action_has_groups(self, action) == True:
                for fcurve in action.layers[0].strips[0].channelbag(action.slots[0]).fcurves:
                    if fcurve.group == None:
                        if "pose.bones" not in fcurve.data_path:
                            try:
                                fcurve.group = action.layers[0].strips[0].channelbag(action.slots[0]).groups["Custom Properties"]
                            except:
                                action.layers[0].strips[0].channelbag(action.slots[0]).groups.new("Custom Properties")
                                fcurve.group = action.layers[0].strips[0].channelbag(action.slots[0]).groups["Custom Properties"]

        return {'FINISHED'}

class CopyGroupstoAll(bpy.types.Operator):
    """Copies the curve group layout from the master action to all actions"""
    bl_idname = "anim.copy_groups_to_all"
    bl_label = "CopyGroupstoAll"
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):

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
        if context.scene.use_selected == False:
            actions = bpy.data.actions
        else:
            if check_active_action(self) == False:
                return {'CANCELLED'}
            actions = [bpy.context.active_object.animation_data.action]

        for action in actions:
            if check_action_has_groups(self, action) == True:
                if action == master_action:
                    continue
                unreferenced_groups = []
                for grp in action.layers[0].strips[0].channelbag(action.slots[0]).groups:
                    if grp.name in master_groups:
                        continue
                    else:
                        unreferenced_groups.append(grp) 
                        try:
                            unreferenced_actions_groups_dict[action.name].append(grp.name) 
                        except:
                            unreferenced_actions_groups_dict[action.name] = [grp.name]
                for grp in master_groups:
                    try:
                        grp_ref = action.layers[0].strips[0].channelbag(action.slots[0]).groups[grp]
                    except: 
                        try:
                            missing_actions_groups_dict[action.name].append(grp)
                        except:
                            missing_actions_groups_dict[action.name] = [grp]
                        continue
                    readd_curve(action, grp_ref)
                for grp_ref in unreferenced_groups:
                     readd_curve(action, grp_ref)               

         
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



CLASSES =  [AlphabetiseAll, CopyGroupstoAll, SortbyRigHierarchy, GroupCustomProperties, GroupOrphanedCurves]

def register_operators():
    for klass in CLASSES:
        bpy.utils.register_class(klass)

def unregister_operators():
    for klass in CLASSES:
        bpy.utils.unregister_class(klass)



if __name__ == '__main__':
    register_operators()
                        
