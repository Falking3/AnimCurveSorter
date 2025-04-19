import importlib
import bpy

if "operators" in locals():
    importlib.reload(operators)
if "ui" in locals():
    importlib.reload(ui)


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


