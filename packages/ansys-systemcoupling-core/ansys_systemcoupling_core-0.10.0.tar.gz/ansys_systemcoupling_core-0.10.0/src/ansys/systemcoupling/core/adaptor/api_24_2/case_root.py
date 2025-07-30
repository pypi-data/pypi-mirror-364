#
# This is an auto-generated file.  DO NOT EDIT!
#

SHASH = "34d232b251e1d4a5a6b88e3deb9591863eac6afb1446228951276f9b1700da9f"

from ansys.systemcoupling.core.adaptor.impl.types import *

from ._clear_state import _clear_state
from .clear_state import clear_state
from .delete_snapshot import delete_snapshot
from .open import open
from .open_snapshot import open_snapshot
from .save import save
from .save_snapshot import save_snapshot


class case_root(Container):
    """
    'root' object
    """

    syc_name = "CaseCommands"

    command_names = [
        "_clear_state",
        "clear_state",
        "delete_snapshot",
        "open",
        "open_snapshot",
        "save",
        "save_snapshot",
    ]

    _clear_state: _clear_state = _clear_state
    """
    _clear_state command of case_root.
    """
    clear_state: clear_state = clear_state
    """
    clear_state command of case_root.
    """
    delete_snapshot: delete_snapshot = delete_snapshot
    """
    delete_snapshot command of case_root.
    """
    open: open = open
    """
    open command of case_root.
    """
    open_snapshot: open_snapshot = open_snapshot
    """
    open_snapshot command of case_root.
    """
    save: save = save
    """
    save command of case_root.
    """
    save_snapshot: save_snapshot = save_snapshot
    """
    save_snapshot command of case_root.
    """
