# CONFERENCE CRAWLER
This code provides a crawler for conferences using [DBLP](https://dblp.org/db/conf/index.html) and [OpenAlex API](https://docs.openalex.org). 

The papers data that this crawler obtains is saved on a JSON file using the following format:

```json
[
    {
        "Year": 2022,
        "Title": "Paper Title",
        "Authors and Institutions": {
            "Author_1": {
                "Institution_1": "Country_1",
                "Institution_2": "Country_2"
            },
            "Author_2": {
                "Institution_2": "Country_2"
            }
        }
    }
]
```

Later you can save the previous data on a DataBase file using the functions defined on the file ``create_db.py``. This python file uses the JSON files created previously to extract the data and create a DB. 
The DB is created and can be manipulated using SQL queries and the library SQLite3.

## HOW TO ADD A NEW CONFERENCE TO THE CRAWLER

If you want to crawl a certain conference, you need to simply go to dblp and search for the conference. 
Then you will have to extract the name that this conference has on its link. 

For example: 
dblp.org/db/conf/**THIS_IS_THE_NAME_YOU_WILL_NEED**/index.html

> https://dblp.org/db/conf/middleware/index.html -> for Middleware is simply **middleware**

> https://dblp.org/db/conf/cloud/index.html -> for Socc (Symposium on Cloud Computing) is **cloud**


### What changes do you need to do to add a new conference?

1. Extract the name from the link, like I have shown.
2. Add the name to the list **conferences** on the file `global_data.py`
3. Add the conference to the **GetPapers**. You may encounter two different options:
	1. The conference data can be crawled with the **GeneralCrawler**: If that's the case, you won't have to do anything.
	2. The conference data needs a specific crawler: If this happens, you will have to implement the crawler, and then add it to the Factory by just adding a new option, and returning the instance.
4. Use the functions in the main file to obtain the data and store it on the format of your preference. There are two formats available in the main file, database and json.
5. If you want the program committee data for the conference, you will have to implement the crawler.