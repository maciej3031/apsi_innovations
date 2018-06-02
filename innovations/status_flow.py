from innovations.models import Innovation
from signup.groups import committee_members, administrators, in_groups


def all_innovation_statuses():
    return [
        getattr(Innovation.Status, status)
        for status in dir(Innovation.Status)
        if isinstance(status, str) and not status.startswith("__")
    ]


_s = Innovation.Status
_both = [committee_members, administrators]
_only_committee = [committee_members]
_only_admin = [administrators]
STATUS_FLOW_MATRIX = {
    _s.PENDING: {"follows": [_s.IN_REPLENISHMENT], "set_by": _both, "substantiation_needed": False},
    _s.IN_REPLENISHMENT: {"follows": [_s.PENDING, _s.VOTING], "set_by": _only_committee, "substantiation_needed": True},
    _s.BLOCKED: {"follows": [_s.PENDING, _s.VOTING], "set_by": _both, "substantiation_needed": True},
    _s.ACCEPTED: {"follows": [_s.VOTING, _s.SUSPENDED], "set_by": _only_committee, "substantiation_needed": True},
    _s.REJECTED: {"follows": [_s.VOTING, _s.SUSPENDED], "set_by": _only_committee, "substantiation_needed": True},
    _s.SUSPENDED: {"follows": [_s.VOTING], "set_by": _only_committee, "substantiation_needed": True},
    _s.VOTING: {"follows": [_s.PENDING], "set_by": _both, "substantiation_needed": False},
}


def try_update_status(user, innovation, new_status, substantiation=""):
    conditions = STATUS_FLOW_MATRIX[new_status]
    user_permitted = in_groups(user, conditions["set_by"])
    status_flow_correct = innovation.status in conditions["follows"]
    substantiation_correct = substantiation != "" or not conditions["substantiation_needed"]
    if user_permitted and status_flow_correct and substantiation_correct:
        innovation.status = new_status
        innovation.substantiation = substantiation
        innovation.save()
        return True
    else:
        return False


def available_status_choices(user, innovation):
    return [
        (status, desc) for status, desc in Innovation.STATUS_CHOICES
        if innovation.status in STATUS_FLOW_MATRIX[status]["follows"]
           and in_groups(user, STATUS_FLOW_MATRIX[status]["set_by"])
    ]
