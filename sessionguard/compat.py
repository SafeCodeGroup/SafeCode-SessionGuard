"""Small shims for third-party library drift."""

import types


def ensure_gobject_idle_add() -> None:
    """Make sure GObject.idle_add exists, as pystray 0.19.5 calls it.

    PyGObject only provides it through its Python overrides (deprecated alias
    of GLib.idle_add). If the overrides are unavailable, GLib.idle_add is the
    raw introspected function, which takes the priority first.
    """
    try:
        from gi.repository import GLib, GObject
    except Exception:
        return  # no PyGObject: pystray uses another backend
    if hasattr(GObject, "idle_add"):
        return
    if isinstance(GLib.idle_add, types.FunctionType):  # PyGObject override
        GObject.idle_add = GLib.idle_add
        return

    def idle_add(function, *user_data, priority=GLib.PRIORITY_DEFAULT_IDLE):
        return GLib.idle_add(priority, function, *user_data)

    GObject.idle_add = idle_add
