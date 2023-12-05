import abc
import requests
from bs4 import BeautifulSoup
import json

class AbstractConferenceCrawler(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def search(self):
        pass

    def _get_links(self, conference):
        # obtain the links for every year
        url = "https://dblp.org/db/conf/" + conference + "/"
        html_page = requests.get(url, timeout=10)
        soup = BeautifulSoup(html_page.text, 'html.parser')
        link_list = set()
        print(f"Conference: {conference}")
        for link_elem in soup.findAll('a'):
            link = link_elem.get('href')
            if link and url in link:  # to avoid repeated links
                link_list.add(link)
        return link_list  # list with all the papers for each year

    def _get_pub_list(self, link):
        resp = requests.get(link, timeout=10)
        soup = BeautifulSoup(resp.content, features="lxml")
        return soup.findAll("ul", attrs={"class": "publ-list"})