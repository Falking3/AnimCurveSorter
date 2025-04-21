if "bpy" in locals():
    import importlib
    for mod in [operators, ui]:
        importlib.reload(mod)
else:
    import bpy
    from. import (operators, ui)



def register():
    from .operators import register_operators
    register_operators()

    from .ui import register_ui
    register_ui()


def unregister():
    from .operators import unregister_operators
    unregister_operators()

    from .ui import unregister_ui
    unregister_ui()


