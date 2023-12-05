import requests
from bs4 import BeautifulSoup

BASE_URL_INSTITUTIONS = "https://api.openalex.org/institutions?search="

def bs4_result_from_link(link):
    response_committee = requests.get(link)
    return BeautifulSoup(response_committee.text, "html.parser")


def search_institution_country(institution):
    institution_country = None
    ins = institution.replace("&", "and")
    response = requests.get(BASE_URL_INSTITUTIONS + ins)
    res = response.json()
    if res['results']:
        ins = res['results'][0]
        institution_country = ins['country_code']
    return institution_country


class NsdiCommittee:

    def get_committee_data(self):
        inst_country = None
        committee_data = {}
        for year in range(2012, 2023):
            member_inst = {}
            url = f"https://www.usenix.org/conference/nsdi{year % 100}/call-for-papers"
            if year == 2012: url = f"https://www.usenix.org/conference/nsdi{year % 100}/call-for-papers-0"
            response = bs4_result_from_link(url)
            committee = response.findAll("div", class_="views-field views-field-field-speakers-institution")
            for elem in committee:
                member = elem.text.split(",")[0].replace('\xa0', ' ').strip()
                institution = elem.text.split(",")[1].strip() if len(elem.text.split(",")) > 1 else None
                if institution is not None: inst_country = search_institution_country(institution.strip())
                member_inst[member.strip()] = {institution:inst_country}
            data = {"Year":year, "Members": member_inst}
            committee_data[data["Year"]] = data["Members"]
        return committee_data
