"""
AUDIT_INFORMATION.GAAP.UNMODIFIED_OPINION
=> "Unmodified opinion"
"""
from django.utils.translation import gettext as _


"""
[[[cog
import json
import cog
from cogutils import (
    TRIPLEQ,
    cognamingclass,
    load_semiconstants_path,
    to_screaming_snake,
)

semiconstants = load_semiconstants_path()
rawjson = semiconstants.joinpath(
    "..",
    "schemas",
    "output",
    "audit",
    "audit-info-values.json",
).read_text("utf-8")

gaapdata = json.loads(rawjson).get("gaap_results")

class_name = "GAAP"
class_doc = "Permitted values for questions on Audit information form."
_properties = tuple([to_screaming_snake(item['tag']) for item in gaapdata])
_keys = tuple([item['tag'] for item in gaapdata])
_values = tuple([item['readable'] for item in gaapdata])

cog.outl("")
cog.outl("")
cog.outl("class AUDIT_INFORMATION:")
cog.outl("    " + TRIPLEQ)
cog.outl("    Permitted values for GAAP questions on Audit information form.")
cog.outl("    " + TRIPLEQ)
cog.outl("")
cognamingclass(
    class_name,
    class_doc,
    list(zip(_properties, _keys, _values)),
    indent="    ",
    i18n=True,
)
]]]"""


class AUDIT_INFORMATION:
    """
    Permitted values for GAAP questions on Audit information form.
    """

    class GAAP:
        """Permitted values for questions on Audit information form."""

        UNMODIFIED_OPINION = "unmodified_opinion"
        QUALIFIED_OPINION = "qualified_opinion"
        ADVERSE_OPINION = "adverse_opinion"
        DISCLAIMER_OF_OPINION = "disclaimer_of_opinion"
        NOT_GAAP = "not_gaap"

        _properties = (
            "UNMODIFIED_OPINION",
            "QUALIFIED_OPINION",
            "ADVERSE_OPINION",
            "DISCLAIMER_OF_OPINION",
            "NOT_GAAP",
        )

        _keys = (
            "unmodified_opinion",
            "qualified_opinion",
            "adverse_opinion",
            "disclaimer_of_opinion",
            "not_gaap",
        )

        _values = (
            _("Unmodified opinion"),
            _("Qualified opinion"),
            _("Adverse opinion"),
            _("Disclaimer of opinion"),
            _("Financial statements were not prepared in accordance with GAAP but were prepared in accordance with a special purpose framework."),
        )

        class _friendly_class:
            """Friendly names class for GAAP"""

            UNMODIFIED_OPINION = "Unmodified opinion"
            QUALIFIED_OPINION = "Qualified opinion"
            ADVERSE_OPINION = "Adverse opinion"
            DISCLAIMER_OF_OPINION = "Disclaimer of opinion"
            NOT_GAAP = "Financial statements were not prepared in accordance with GAAP but were prepared in accordance with a special purpose framework."

        _friendly_tuple = tuple(zip(_keys, _values))

        _friendly_dict = dict(_friendly_tuple)


# [[[end]]]
