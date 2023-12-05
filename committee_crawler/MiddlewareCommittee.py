from bs4 import BeautifulSoup
import requests

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

class MiddlewareCommittee:

    def get_committee_data(self):
        committee_data = {}
        committee_data[self.get_committee_2014()["Year"]] = self.get_committee_2014()["Members"]
        committee_data[self.get_committee_2016()["Year"]] = self.get_committee_2016()["Members"]
        committee_data[self.get_committee_2018()["Year"]] = self.get_committee_2018()["Members"]
        committee_data[self.get_committee_2019()["Year"]] = self.get_committee_2019()["Members"]
        committee_data[self.get_committee_2020()["Year"]] = self.get_committee_2020()["Members"]
        committee_data[self.get_committee_2021()["Year"]] = self.get_committee_2021()["Members"]
        committee_data[self.get_committee_2022()["Year"]] = self.get_committee_2022()["Members"]
        return committee_data

    def get_committee_2022(self):
        committee = bs4_result_from_link("https://middleware-conf.github.io/2022/program-committee/")
        committee_members = committee.find_all("li", align="justify")

        members_inst = {}
        for i in committee_members:
            text = i.text.split(",")
            institution = text[1].strip()
            inst_country = search_institution_country(institution)
            members_inst[text[0].strip()] = {institution:inst_country}
        return {"Year":2022, "Members": members_inst}

    def get_committee_2021(self):
        committee = bs4_result_from_link("https://middleware-conf.github.io/2021/program-committee/")
        committee_members = committee.find_all("li", align="justify")

        members_inst = {}
        for i in committee_members:
            text = i.text.split(",")
            institution = text[1].strip()
            inst_country = search_institution_country(institution)
            members_inst[text[0].strip()] = {institution:inst_country}
        return {"Year":2021, "Members": members_inst}

    def get_committee_2020(self):
        committee = bs4_result_from_link("https://2020.middleware-conference.org/program-committee.html")
        committee_members = committee.findAll("p", class_="align-center")

        members_inst = {}
        for i in committee_members:
            text = i.text.split(",")
            institution = text[1].strip()
            inst_country = search_institution_country(institution)
            members_inst[text[0].strip()] = {institution:inst_country}
        return {"Year":2020, "Members": members_inst}

    def get_committee_2019(self):
        committee = bs4_result_from_link("https://2019.middleware-conference.org/program.html")
        committee_members = committee.findAll("div", class_="cbp-item web-design graphic print motion")

        members_inst = {}
        for i in committee_members:
            member = i.find("div", class_="cbp-l-caption-title").text
            institution = i.find("div", class_="cbp-l-caption-desc").text
            inst_country = search_institution_country(institution.strip())
            members_inst[member.strip()] = {institution.strip():inst_country}
        return {"Year":2019, "Members": members_inst}

    def get_committee_2018(self):
        committee = bs4_result_from_link("http://2018.middleware-conference.org/index.php/program-committee/")
        co_chairs = committee.findAll("p")[0].text.replace("\t", "").replace("\n", ",").split(",")
        committee = committee.findAll("p")[1].text.replace("\t", "").replace("\n", ",").split(",")
        committee_members = co_chairs + committee

        members_inst = {}
        cont = 1
        for elem in committee_members:
            if cont == 1:
                member_name = elem
            if cont == 2:
                institution = elem.strip()
            if cont == 3:
                cont = 0
                inst_country = search_institution_country(institution.strip())
                members_inst[member_name.strip()] = {institution.strip():inst_country}
            if elem == " Université catholique de Louvain":
                cont = 0
                inst_country = search_institution_country(institution.strip())
                members_inst[member_name.strip()] = {institution.strip():inst_country}
            cont += 1
        return {"Year":2018, "Members": members_inst}

    def get_committee_2016(self):
        committee = bs4_result_from_link("http://2016.middleware-conference.org/organization/tpc/")

        committee_members = committee.find("table")

        members_inst = {}
        for elem in committee_members:
            if elem != "\n":
                member = elem.find("strong").text
                institution = elem.find("span").text.split(",")[0]
                inst_country = search_institution_country(institution.strip())
                members_inst[member.strip()] = {institution.strip():inst_country}
        return {"Year":2016, "Members": members_inst}

    def get_committee_2014(self):
        committee = bs4_result_from_link("https://middleware-conf.github.io/2014/committees/program/")
        co_chairs = committee.findAll("ul")[5].findAll("li")
        members = committee.findAll("ul")[6].findAll("li")
        committee_members = co_chairs + members

        members_inst = {}
        for elem in committee_members:
            member = elem.text.split(";")[0]
            institution = elem.text.split(";")[1].split(",")[0]
            inst_country = search_institution_country(institution.strip())
            members_inst[member.strip()] = {institution.strip():inst_country}
        return {"Year":2014, "Members": members_inst}