"""
AUDIT_TYPE.SINGLE_AUDIT
=> "single-audit"

AUDIT_TYPE._friendly_tuple
=> (
    ("single-audit", _("Single Audit")),
    ("program-specific", _("Program-Specific Audit")),
)
# The above is the format that Django expects for choices in models, for example.

AUDIT_TYPE._friendly_dict.get("single-audit")
=> _("Single Audit")

AUDIT_TYPE._friendly_class.PROGRAM_SPECIFIC
=> _("Program-Specific Audit")
"""
from django.utils.translation import gettext as _

"""
[[[cog
import cog
from cogutils import cognamingclass

class_name = "AUDIT_TYPE"
class_doc = "Permitted values for audit type."

_properties = (
    "SINGLE_AUDIT",
    "PROGRAM_SPECIFIC",
)

_keys = (
    "single-audit",
    "program-specific",
)

_values = (
    "Single Audit",
    "Program-Specific Audit",
)

cog.outl("")
cog.outl("")
cognamingclass(class_name, class_doc, list(zip(_properties, _keys, _values)), indent="", i18n=True)
]]]"""


class AuditType:
    """Permitted values for audit type."""

    SINGLE_AUDIT = "single-audit"
    PROGRAM_SPECIFIC = "program-specific"

    _properties = (
        "SINGLE_AUDIT",
        "PROGRAM_SPECIFIC",
    )

    _keys = (
        "single-audit",
        "program-specific",
    )

    _values = (
        _("Single Audit"),
        _("Program-Specific Audit"),
    )

    class FriendlyClass:
        """Friendly names class for AUDIT_TYPE"""

        SINGLE_AUDIT = "Single Audit"
        PROGRAM_SPECIFIC = "Program-Specific Audit"

    _friendly_type = FriendlyClass

    _friendly_tuple = tuple(zip(_keys, _values))

    _friendly_dict = dict(_friendly_tuple)


# [[[end]]]
