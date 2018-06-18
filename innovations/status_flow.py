from collections import Counter

from innovations.models import Innovation, StatusVote
from signup.groups import committee_members, administrators, in_groups, get_number_of_members


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


def available_statuses(user, innovation):
    return [status for status, desc in available_status_choices(user, innovation)]


def available_statuses_for_comittee(innovation):
    return [
        status for status, _ in Innovation.STATUS_CHOICES
        if innovation.status in STATUS_FLOW_MATRIX[status]["follows"]
           and committee_members in STATUS_FLOW_MATRIX[status]["set_by"]
    ]


def try_finish_status_voting(innovation):
    status_votes = innovation.status_votes.all()
    counter = Counter([vote.proposed_status for vote in status_votes])
    threshold = get_number_of_members(committee_members) / 2
    for status, votes_number in counter.items():
        if votes_number > threshold:
            has_been_updated = try_update_status(
                user=committee_members.user_set.last(),
                innovation=innovation,
                new_status=status,
                substantiation=get_substantiation(innovation)
            )
            if has_been_updated:
                status_votes.delete()
                return True
    return False


def get_status_votes_counter(innovation):
    status_votes = innovation.status_votes.all()
    counter = Counter([vote.proposed_status for vote in status_votes])
    for status in available_statuses_for_comittee(innovation):
        if status not in counter:
            counter[status] = 0
    return counter


def get_status_votes_table(innovation):
    counter = get_status_votes_counter(innovation)
    number_of_committee_members = get_number_of_members(committee_members)
    result = {
        "headers": ["Status", "Votes", "Max", "Percentage", "Substantiation"],
        "rows": [
            [
                s,
                v,
                number_of_committee_members,
                "{}%".format((v / number_of_committee_members) * 100),
                get_substantiation(innovation, status=s)
            ] for s, v in counter.items()
        ]
    }
    return result


def get_substantiation(innovation, status=None):
    statuses = innovation.status_votes.all().filter(substantiation__iregex=".+")
    if status:
        statuses = statuses.filter(proposed_status=status)
    last_status = statuses.last()
    return last_status.substantiation if last_status else ""
