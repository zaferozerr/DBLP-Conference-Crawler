from conference_crawler.general_crawler import GeneralCrawler
from conference_crawler.nsdi_crawler import NsdiCrawler


class GetCrawler:

    def getCrawler(self, conference):
        if conference == "nsdi":
            return NsdiCrawler(conference)
        else:
            return GeneralCrawler(conference)