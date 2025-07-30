from typing import Final
from volworld_common.api.CA import CA


# ====== A: Attribute ======
class AA(CA):

    Bar: Final[str] = "bar"
    BottomAppBar: Final[str] = "btmab"

    CheckBox: Final[str] = "chkbx"
    Circle: Final[str] = "cce"

    Edit: Final[str] = "edt"
    Editor: Final[str] = "edr"
    Existing: Final[str] = "extg"

    Filled: Final[str] = "fld"

    LearnerRefWf: Final[str] = "lwf"
    LearnerSaLogId: Final[str] = "lrsalid"
    Left: Final[str] = "lft"
    Link: Final[str] = "lnk"
    Load: Final[str] = "lod"
    Logout: Final[str] = "lgo"

    Memorized: Final[str] = "mmd"
    MoreActions: Final[str] = "mact"

    Switch: Final[str] = "sth"

    Waiting: Final[str] = "wtg"

AAList = [AA, CA]
