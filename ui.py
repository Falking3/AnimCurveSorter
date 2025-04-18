import bpy



def actions_settings_callback (scene, context):
    items = [('EMPTY', '_NONE_', '')]
    for action in bpy.data.actions:
        items.append((action.name, action.name, ""))
    return items



PROPS = [ 
    ("master_action", bpy.props.EnumProperty(items = actions_settings_callback, name = "Tpose Action")),
]

class ACS_PT_MainPanel(bpy.types.Panel):
    bl_idname = "ACS_PT_MainPanel"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Anim Curve Sorter"
    bl_label = 'Animation'

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align = True)
        row = col.row (align =True)

        row.operator("animcurvesort.alphabetise_all", text = "Sort All Alphabetically")
        col = box.column(align = True)
        row = col.row (align =True)

        row.label(text = "Master Action")
        row.label(text = "", icon = "ACTION")
        row = col.row (align =True)
        row.prop(context.scene, "master_action", text = "")

        col = box.column(align = True)
        row = col.row (align =True)
        props = row.operator("animcurvesort.copy_groups_to_all", text = "Copy Groups to All")
        props.use_selected = False

        col = box.column(align = True)
        row = col.row (align =True)
        props = row.operator("animcurvesort.copy_groups_to_all", text = "Copy Groups to Active Action")
        props.use_selected = True



CLASSES =  [ACS_PT_MainPanel]

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