from committee_crawler.MiddlewareCommittee import MiddlewareCommittee
from committee_crawler.NsdiCommittee import NsdiCommittee
from committee_crawler.SoccCommittee import SoccCommittee


class GetCommittee:

    def get_committee(self, conference):
        if conference == "nsdi":
            return NsdiCommittee()
        if conference == "middleware":
            return MiddlewareCommittee()
        if conference == "cloud":
            return SoccCommittee()