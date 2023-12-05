import re

import requests
from bs4 import BeautifulSoup
import spacy
from tqdm import tqdm
import global_data
from conference_crawler.AbstarctConferenceCrawler import AbstractConferenceCrawler

BASE_URL_INSTITUTIONS = "https://api.openalex.org/institutions"
nlp = spacy.load("en_core_web_lg")

processed_inst = {}

class NsdiCrawler(AbstractConferenceCrawler):

    def __init__(self, conf):
        self.conference = conf

    def _get_papers_data(self, pub):
        authors = {}
        publication_year = 'nothing'
        paper_title = 'nothing'
        authors_names = {}
        for content_item in pub.contents:
            class_of_content_item = content_item.attrs.get('class', [0])
            if 'data' in class_of_content_item:
                # get the publication year from dblp
                for datePublished in content_item.findAll('span', attrs={"itemprop": "datePublished"}):
                    publication_year = datePublished.text
                if publication_year == 'nothing':
                    publication_year = content_item.find('meta', attrs={"itemprop": "datePublished"}).get("content")
                # get the paper title from dblp
                paper_title = content_item.find('span', attrs={"class": "title", "itemprop": "name"}).text
            # get the author's names from dblp paper
            for author in content_item.findAll('span', attrs={"itemprop": "author"}):
                author_name = author.text
                authors_names[author_name] = None
            #get all the paper links to crawl the data
            if 'publ' in class_of_content_item:
                links = content_item.contents[0].findAll("a")
                link = [l.get("href") for l in links if "usenix" in l.get("href")]
                if not link:    # if there's no link, return the obtained information
                    return {'Year': int(publication_year) if publication_year != "nothing" else publication_year,
                            'Title': paper_title,
                            'Authors and Institutions': authors}
        # obtain all the aouthor's information
        authors_info = self._get_usenix_authors_inst(link[0])
        if authors_info is None:    #if there's no information, just return the author's names
            authors = authors_names
        else:   # if there's information
            for author in authors_info:     # obtain the institution information
                inst = authors_info[author].replace("&", "and")
                auth_inst = self._get_institution_countries(inst)
                authors[author] = auth_inst

        return {'Year':int(publication_year),
                'Title': paper_title,
                'Authors and Institutions': authors}


    def _get_usenix_authors_inst(self, link):
        resp = requests.get(link)
        soup = BeautifulSoup(resp.text, 'html.parser')
        auth_data = soup.find("div", class_="field-item odd")
        members_inst = {}
        try:
            for child in auth_data:
                unprocessed_data = child.text.split("\n")[0]
                institution = []
                for em_tag in child.find_all('em'):
                    elem = em_tag.text.replace(";", "").strip()
                    ins = re.sub(r'[^\x00-\x7F]+', '', elem)
                    institution.append(ins)
                authors = unprocessed_data.split(";")
                for ind, author in enumerate(authors):
                    splited_data = author.split(",")
                    for i, data in enumerate(splited_data):
                        splited_data[i] = data.strip()
                        splited_data[i] = re.sub(r'[^\x00-\x7F]+', '', splited_data[i])
                    if "," in institution[ind]:
                        splited_ins = institution[ind].split(",")
                        institution[ind] = institution[ind].split(",")[0]
                        for ins in splited_ins:
                            splited_data.remove(ins.strip())  # list of the authors without the institutions
                    else:
                        splited_data.remove(institution[ind])  # list of the authors without the institutions

                    for data in splited_data:
                        doc = nlp(data.strip())
                        for token in doc:
                            if token.pos_ == "CCONJ":
                                data = data.replace(token.text, ",")

                        authors = data.split(",")
                        name = [a.strip() for a in authors if a != ""]
                        for a in name:
                            members_inst[a] = institution[ind]
        except Exception:
            return None
        return members_inst


    def _get_url_response(self, inst):
        response = requests.get(BASE_URL_INSTITUTIONS + f'?search={inst}')
        data = response.json()
        return data['results']


    def _get_institution_countries(self, inst):
        institution_data = {}
        if inst not in processed_inst:
            results = self._get_url_response(inst)
            if results:
                final_result = results[0]
                institution_name = final_result['display_name']
                institution_country = final_result['country_code']
                institution_data[institution_name] = institution_country
                processed_inst[inst] = [institution_name,institution_country]
            else:
                institution_name = inst
                institution_country = None
                institution_data[institution_name] = institution_country
        else:
            institution_name = processed_inst[inst][0]
            institution_country = processed_inst[inst][1]
            institution_data[institution_name] = institution_country

        return institution_data


    def search(self):
        links = super()._get_links(self.conference)

        data = []
        links = [link for link in links if (any(str(year) in link for year in range(global_data.FIRST_YEAR, global_data.LAST_YEAR + 1)))]
        for link in tqdm(links):
            pub_list_raw = super()._get_pub_list(link)
            for pub in pub_list_raw:
                for child in pub:
                    pub_data = self._get_papers_data(child)
                    if pub_data is not None: data.append(pub_data)
        return data