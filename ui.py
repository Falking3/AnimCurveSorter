import bpy

def actions_settings_callback (scene, context):
    items = [('EMPTY', '_NONE_', '')]
    for action in bpy.data.actions:
        items.append((action.name, action.name, ""))
    return items

def panel_layout(self, context):
    layout = self.layout
    box = layout.box()
    col = box.column(align = True)
    col.prop(bpy.context.scene, "use_selected", text = "Apply Only to Active Action?")

    box = layout.box()
    col = box.column(align = True)
    col.operator("animcurvesort.alphabetise_all", text = "Sort All Actions Alphabetically", icon = "SORTALPHA")
    col.operator("animcurvesort.sort_by_rig", text = "Sort All Actions by Rig Hierarchy", icon = "OUTLINER_OB_ARMATURE")

    box = layout.box()
    col = box.column(align = True)
    col.operator("animcurvesort.copy_groups_to_all", text = "Copy Groups to All Actions", icon = "COPYDOWN")

    col = box.column(align = True)
    row = col.row (align =True)
    row.label(text = "Action to Copy From")
    row.label(text = "", icon = "ACTION")
    row = col.row (align =True)
    row.prop(context.scene, "master_action", text = "")



    box = layout.box()
    col = box.column(align = True)
    col.operator("animcurvesort.group_orphaned_curves", text = "Group Orphaned Curves", icon = "FCURVE")
    col.operator("animcurvesort.group_custom_properties", text = "Group Non-Bone Custom Properties", icon = "PROPERTIES")


PROPS = [ 
    ("master_action", bpy.props.EnumProperty(items = actions_settings_callback, name = "Master Action")),
    ("use_selected",  bpy.props.BoolProperty(name = "UseSelected?", default = False)),
]

class ACS_PT_GraphPanel(bpy.types.Panel):
    bl_idname = "ACS_PT_GraphPanel"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Anim Curve Sorter"
    bl_label = 'Sort Curve Groups'

    def draw(self, context):
        panel_layout(self,context)

class ACS_PT_ActionPanel(bpy.types.Panel):
    bl_idname = "ACS_PT_ActionPanel"
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Anim Curve Sorter"
    bl_label = 'Sort Curve Groups'

    def draw(self, context):
        panel_layout(self,context)



CLASSES =  [ACS_PT_GraphPanel, ACS_PT_ActionPanel]

for (prop_name, prop_value) in PROPS:
    setattr(bpy.types.Scene, prop_name, prop_value)

def register_ui():
    for klass in CLASSES:
        bpy.utils.register_class(klass)

def unregister_ui():
    for klass in CLASSES:
        bpy.utils.unregister_class(klass)



if __name__ == '__main__':
    register_ui()