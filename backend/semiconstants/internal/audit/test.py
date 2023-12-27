"""
SUBMISSION_STATUS.IN_PROGRESS
=> "In Progress"

SUBMISSION_STATUS._friendly_tuple
=> (('in_progress', 'In Progress'), ('ready_for_certification', 'Ready for Certification'), ('auditor_certified', 'Auditor Certified'), ('auditee_certified', 'Auditee Certified'), ('certified', 'Certified'), ('submitted', 'Submitted'), ('disseminated', 'Disseminated'))
# The above is the format that Django expects for choices in models, for example.

SUBMISSION_STATUS._friendly_dict.get("in_progress")
=> "In Progress"

SUBMISSION_STATUS._friendly_class.CERTIFIED
=> "Certified"


[[[cog
import cog
from ..cogutils import cognamingclass

class_name = "SUBMISSION_STATUS"
class_doc = "The states that a submission can be in."

_properties = (
    "IN_PROGRESS",
    "READY_FOR_CERTIFICATION",
    "AUDITOR_CERTIFIED",
    "AUDITEE_CERTIFIED",
    "CERTIFIED",
    "SUBMITTED",
    "DISSEMINATED",
)

_keys = (
    "in_progress",
    "ready_for_certification",
    "auditor_certified",
    "auditee_certified",
    "certified",
    "submitted",
    "disseminated",
)

_values = (
    "In Progress",
    "Ready for Certification",
    "Auditor Certified",
    "Auditee Certified",
    "Certified",
    "Submitted",
    "Disseminated",
)

cog.outl("")
cog.outl("")
cognamingclass(class_name, class_doc, list(zip(_properties, _keys, _values)), indent="")
]]]"""
