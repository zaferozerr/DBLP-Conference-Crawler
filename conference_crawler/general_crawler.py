import requests
from tqdm import tqdm
import global_data
from conference_crawler.AbstarctConferenceCrawler import AbstractConferenceCrawler


BASE_URL_INSTITUTIONS = "https://api.openalex.org/institutions"
BASE_URL_WORKS = "https://api.openalex.org/works/"

class GeneralCrawler(AbstractConferenceCrawler):

    def __init__(self, conf):
        self.conference = conf


    def _search_institution(self, id):
        # get the OpenAlex API response for the institution name
        response = requests.get(BASE_URL_INSTITUTIONS + id)
        return response.json()


    def _get_papers_data_link(self, pub):
        # obtain the OpenAlex API link from each paper
        for content_item in pub.contents:
            class_of_content_item = content_item.attrs.get('class', [0])
            if 'publ' in class_of_content_item:
                links = content_item.contents[0].findAll("a")
                link = [l.get("href") for l in links if "openalex" in l.get("href")]
                response = requests.get(link[0]) if link != [] else None
                return response


    def _get_papers_data(self, pub):
        response_data = self._get_papers_data_link(pub)

        if response_data is None:   # if there is not OpenAlex link
            return None

        response_data = response_data.json()
        publication_year = response_data['publication_year']    # obtain the publiation year from the paper
        paper_title = response_data['title']    # obtain the title from the paper

        authors = {}
        authorships = response_data['authorships']  # obtain all the authors from the paper
        for author in authorships:
            institution_data = {}
            institution_country = None
            author_display_name = author['author']['display_name']  # obtain the author's name
            author_institutions = author['institutions']    # obtain the author's possible institutions
            if author['countries']:     #obtain the country of those institutions
                institution_country = author['countries'][0]

            if author_institutions:     # if the author has some institution affiliated
                for institution in author_institutions:
                    institution_id = institution['id'].split("/")[3]
                    institution_info = self._search_institution(f"/{institution_id}")   # search the institution id on the OpenAlex API
                    institution_name = institution_info['display_name']    # get the institution name
                    institution_country = institution_info['country_code']      # get the institution country
                    institution_data[institution_name] = institution_country if institution_country != [] else None

            if not author_institutions: # if the author does not have any institution affiliated
                institution_name = author['raw_affiliation_string']
                if institution_name == "":  # institution name is None in case there's no name
                    institution_data = None
                else:
                    raw_institution_name = institution_name.replace("&", "and")
                    res = self._search_institution(f"?search={raw_institution_name}")   # search the institution name on OpenAlex API
                    if res['results']:  # if we found some information about the institution
                        ins = res['results'][0]
                        institution_country = ins['country_code']   # get the institution country
                    institution_data[institution_name] = institution_country if institution_country != [] else None

            authors[author_display_name] = institution_data     # save all the author data
        return {'Year':int(publication_year),
                'Title': paper_title,
                'Authors and Institutions': authors}



    def search(self):
        links = super()._get_links(self.conference)
        data = []
        # get the links for ONE year only
        links = [link for link in links if (any(str(year) in link for year in range(global_data.FIRST_YEAR, global_data.LAST_YEAR + 1)))]
        for link in tqdm(links):    # start crawling for each link
            pub_list_raw = super()._get_pub_list(link)
            for list in pub_list_raw:
                for child in list:
                    pub_data = self._get_papers_data(child)
                    if pub_data is not None: data.append(pub_data)
        return data