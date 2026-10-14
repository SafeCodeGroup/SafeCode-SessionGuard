"""Small shims for third-party library drift."""


def ensure_gobject_idle_add() -> None:
    """pystray 0.19.5 calls GObject.idle_add, which current PyGObject removed.

    GLib.idle_add is the same function under its supported name.
    """
    try:
        from gi.repository import GLib, GObject
    except Exception:
        return  # no PyGObject: pystray uses another backend
    if not hasattr(GObject, "idle_add"):
        GObject.idle_add = GLib.idle_add
