import bpy


class AlphabetiseAll(bpy.types.Operator):
    """Sorts curve groups in all actions by alphabetical order"""
    bl_idname = "animcurvesort.alphabetise_all"
    bl_label = "AlphabetiseAll"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        for action in bpy.data.actions:
            group_list = []
            for grp in action.layers[0].strips[0].channelbag(action.slots[0]).groups:
                group_list.append(grp.name)
            sorted_group_list = sorted(group_list, key=str.casefold)
            for grp in sorted_group_list:
                curves = []
                grp_ref = action.layers[0].strips[0].channelbag(action.slots[0]).groups[grp]
                for curve in grp_ref.channels:
                    curves.append(curve)
                action.groups.remove(grp_ref)
                newgrp = action.layers[0].strips[0].channelbag(action.slots[0]).groups.new(grp)
                for curve in curves:
                    curve.group = newgrp

        return {'FINISHED'}


class CopyGroupstoAll(bpy.types.Operator):
    """Copies the curve group layout from the master action to all actions"""
    bl_idname = "animcurvesort.copy_groups_to_all"
    bl_label = "CopyGroupstoAll"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        use_selected : bpy.props.BoolProperty(name = "UseSelected?", default = False)

        master_groups = []
        master_action = bpy.data.actions[0]
        for grp in master_action.layers[0].strips[0].channelbag(master_action.slots[0]).groups:
            master_groups.append(grp.name)
            
        missing_actions_groups_dict = {}
        unreferenced_actions_groups_dict = {}
        if use_selected == False:
            actions = bpy.data.actions
        else:
            actions = [bpy.context.active_object.animation_data.action]

        for action in bpy.data.actions:
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
                curves = []
                try:
                    grp_ref = action.layers[0].strips[0].channelbag(action.slots[0]).groups[grp]
                except: 
                    try:
                        missing_actions_groups_dict[action.name].append(grp)
                    except:
                        missing_actions_groups_dict[action.name] = [grp]
                    continue
                for curve in grp_ref.channels:
                    curves.append(curve)
                action.groups.remove(grp_ref)
                newgrp = action.layers[0].strips[0].channelbag(action.slots[0]).groups.new(grp)
                for curve in curves:
                    curve.group = newgrp
            for grp_ref in unreferenced_groups:
                grp = grp_ref.name
                for curve in grp_ref.channels:
                    curves.append(curve)
                action.groups.remove(grp_ref)
                newgrp = action.layers[0].strips[0].channelbag(action.slots[0]).groups.new(grp)
                for curve in curves:
                    curve.group = newgrp 
         
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


CLASSES =  [AlphabetiseAll, CopyGroupstoAll]

def register_operators():
    for klass in CLASSES:
        bpy.utils.register_class(klass)

def unregister_operators():
    for klass in CLASSES:
        bpy.utils.unregister_class(klass)



if __name__ == '__main__':
    register_operators()
                        
