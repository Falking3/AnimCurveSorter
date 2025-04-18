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


CLASSES =  [AlphabetiseAll]

def register_operators():
    for klass in CLASSES:
        bpy.utils.register_class(klass)

def unregister_operators():
    for klass in CLASSES:
        bpy.utils.register_class(klass)



if __name__ == '__main__':
    register_operators()
                        
