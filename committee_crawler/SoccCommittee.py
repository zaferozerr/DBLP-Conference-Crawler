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


class SoccCommittee:

    def get_committee_data(self):
        committee_data = {}
        data = {}
        for year in range(2015, 2023):
            member_inst = {}
            url = f"https://acmsocc.org/{year}/program-committee.html"
            response = bs4_result_from_link(url)
            if year == 2019:
                committee = response.find("ul", style="font-size:110%;").children
                for elem in committee:
                    text = elem.text.split("\n")[0]
                    if not text: continue
                    final_text = text.replace("\t", "").lstrip()
                    member = final_text.split(",")[0]
                    institution = final_text.split(",")[1].replace("  ", " ")
                    inst_country = search_institution_country(institution.strip())
                    member_inst[member.strip()] = {institution.strip():inst_country}
                    data = {"Year":year, "Members": member_inst}
                committee_data[data["Year"]] = data["Members"]
            elif year == 2022:
                # committee = response.find("div", class_="row").children
                committee = response.findAll("div", class_="inner")
                for elem in committee:
                    member = elem.find("header").text.replace("\n", "").strip()
                    institution = elem.find("figure").text.replace("\n", "").strip().replace("  ", " ")
                    inst_country = search_institution_country(institution.strip())
                    member_inst[member.strip()] = {institution.strip():inst_country}
                data = {"Year":year, "Members": member_inst}
                committee_data[data["Year"]] = data["Members"]
            else:
                committee = response.findAll("div", class_="inner")
                for elem in committee:
                    member = elem.text.split("\n")[1]
                    institution = elem.text.split("\n")[2].replace("  ", " ")
                    inst_country = search_institution_country(institution.strip())
                    member_inst[member.strip()] = {institution.strip():inst_country}
                data = {"Year":year, "Members": member_inst}
                committee_data[data["Year"]] = data["Members"]
        return committee_data