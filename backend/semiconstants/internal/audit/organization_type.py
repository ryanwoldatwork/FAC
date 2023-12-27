"""
ORGANIZATION_TYPE.HIGHER_ED
=> "higher-ed"

ORGANIZATION_TYPE._friendly_tuple
=> (
    ("state", _("State")),
    ("local", _("Local Government")),
    ("tribal", _("Indian Tribe or Tribal Organization")),
    ("higher-ed", _("Institution of higher education (IHE)")),
    ("non-profit", _("Non-profit")),
    ("unknown", _("Unknown")),
    ("none", _("None of these (for example, for-profit)")),
)
# The above is the format that Django expects for choices in models, for example.

ORGANIZATION_TYPE._friendly_dict.get("higher-ed")
=> _("Institution of higher education (IHE)")

ORGANIZATION_TYPE._friendly_class.TRIBAL
=> _("Indian Tribe or Tribal Organization")
"""
from django.utils.translation import gettext as _

"""
[[[cog
import cog
from cogutils import cognamingclass

class_name = "ORGANIZATION_TYPE"
class_doc = "Permitted values for organization type."

_properties = (
    "STATE",
    "LOCAL",
    "TRIBAL",
    "HIGHER_ED",
    "NON_PROFIT",
    "UNKNOWN",
    "NONE",
)

_keys = (
    "state",
    "local",
    "tribal",
    "higher-ed",
    "non-profit",
    "unknown",
    "none",
)

_values = (
    "State",
    "Local Government",
    "Indian Tribe or Tribal Organization",
    "Institution of higher education (IHE)",
    "Non-profit",
    "Unknown",
    "None of these (for example, for-profit)",
)

cog.outl("")
cog.outl("")
cognamingclass(class_name, class_doc, list(zip(_properties, _keys, _values)), indent="", i18n=True)
]]]"""


class ORGANIZATION_TYPE:
    """Permitted values for organization type."""

    STATE = "state"
    LOCAL = "local"
    TRIBAL = "tribal"
    HIGHER_ED = "higher-ed"
    NON_PROFIT = "non-profit"
    UNKNOWN = "unknown"
    NONE = "none"

    _properties = (
        "STATE",
        "LOCAL",
        "TRIBAL",
        "HIGHER_ED",
        "NON_PROFIT",
        "UNKNOWN",
        "NONE",
    )

    _keys = (
        "state",
        "local",
        "tribal",
        "higher-ed",
        "non-profit",
        "unknown",
        "none",
    )

    _values = (
        _("State"),
        _("Local Government"),
        _("Indian Tribe or Tribal Organization"),
        _("Institution of higher education (IHE)"),
        _("Non-profit"),
        _("Unknown"),
        _("None of these (for example, for-profit)"),
    )

    class _friendly_class:
        """"""

        STATE = "State"
        LOCAL = "Local Government"
        TRIBAL = "Indian Tribe or Tribal Organization"
        HIGHER_ED = "Institution of higher education (IHE)"
        NON_PROFIT = "Non-profit"
        UNKNOWN = "Unknown"
        NONE = "None of these (for example, for-profit)"


    _friendly_tuple = tuple(zip(_keys, _values))

    _friendly_dict = dict(_friendly_tuple)


# [[[end]]]
