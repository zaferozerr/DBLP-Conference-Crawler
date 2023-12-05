from multiprocessing import Pool
import global_data
from committee_crawler.GetCommittee import GetCommittee
from conference_crawler.GetCrawler import GetCrawler
import json


def save_data_to_json(file_name, data):
    name = f"/data/{file_name}.json"
    with open(name, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def search_conference(conf):
    crawler = GetCrawler()
    results = crawler.getCrawler(conf).search()
    save_data_to_json(f"papers_{conf}", results)


def search_committee(conf):
    crawler = GetCommittee()
    results = crawler.get_committee(conf).get_committee_data()
    save_data_to_json(f"committee_{conf}", results)



if __name__ == "__main__":
    pool = Pool()

    pool.map(search_conference, global_data.conferences)
    pool.map(search_committee, global_data.conferences)

    pool.close()
    pool.join()

