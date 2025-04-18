import bpy


class ACS_PT_GraphEditorPanel(bpy.types.Panel):
    bl_idname = "ACS_PT_GraphEditorPanel"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Anim Curve Sorter"
    bl_label = 'Animation'

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align = True)
        row = col.row (align =True)

        row.operator("animcurvesort.alphabetise_all", text = "Sort all alphabetically")


CLASSES =  [ACS_PT_GraphEditorPanel]

def register_ui():
    for klass in CLASSES:
        bpy.utils.register_class(klass)

def unregister_ui():
    for klass in CLASSES:
        bpy.utils.register_class(klass)



if __name__ == '__main__':
    register_ui()