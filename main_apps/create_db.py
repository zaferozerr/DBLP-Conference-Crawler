import json
import sqlite3
from multiprocessing import Pool
import global_data


def read_json_file (conf):
    # open the json committee/papers file for a certain conference
    with open(f"../data/papers_{conf}.json", "r", encoding="utf-8") as archivo:
        papers_data = json.load(archivo)
    with open(f"../data/committee_{conf}.json", "r", encoding="utf-8") as archivo:
        committee_data = json.load(archivo)
    return papers_data, committee_data


def create_tables(year, conference_name):
    conn = sqlite3.connect(f'../database/{conference_name}.db')
    cursor = conn.cursor()

    cursor.execute(f'''CREATE TABLE IF NOT EXISTS Authors_{year} (
                        id_author INTEGER PRIMARY KEY AUTOINCREMENT,
                        Name TEXT,
                        member BOOLEAN,
                        paper_issuer BOOLEAN
                    )''')

    cursor.execute(f'''CREATE TABLE IF NOT EXISTS Papers_{year} (
                        id_paper INTEGER PRIMARY KEY AUTOINCREMENT,
                        Name TEXT
                    )''')

    cursor.execute(f'''CREATE TABLE IF NOT EXISTS Authors_Papers_{year} (
                        id_author INTEGER,
                        id_paper INTEGER,
                        FOREIGN KEY (id_author) REFERENCES Individuals_{year}(id_author),
                        FOREIGN KEY (id_paper) REFERENCES Papers_{year}(id_paper)
                    )''')

    cursor.execute(f'''CREATE TABLE IF NOT EXISTS Institutions_{year} (
                        id_institution INTEGER PRIMARY KEY AUTOINCREMENT,
                        Name TEXT,
                        Place TEXT
                    )''')

    cursor.execute(f'''CREATE TABLE IF NOT EXISTS Authors_Institutions_{year} (
                        id_author INTEGER,
                        id_institution INTEGER,
                        FOREIGN KEY (id_author) REFERENCES Authors_{year}(id_author),
                        FOREIGN KEY (id_institution) REFERENCES Institutions_{year}(id_institution)
                    )''')
    conn.commit()
    conn.close()
    print(f'Database for {conference_name} {year} created Successfully')


def insert_names_members(args):
    conference_name, name, inst, y = args
    conn = sqlite3.connect(f'../database/{conference_name}.db')

    cursor = conn.cursor()
    try:
        cursor.execute(f'SELECT Name FROM Authors_{y} WHERE Name = ?', (name,))
        existing_name = cursor.fetchone()
        if existing_name is None:
            cursor.execute(f"INSERT INTO Authors_{y} (Name, member, paper_issuer) "
                       f"VALUES (?, 1, 0)", (name, ))
    except Exception as e:
        print(f"Error Insert Author")
        print(e)

    cursor.execute(f'SELECT id_author FROM Authors_{y} WHERE Name = ?', (name,))
    id_author = cursor.fetchone()[0]

    if inst is not None:
        for institution, country in inst.items():
            cursor.execute(f'SELECT Name FROM Institutions_{y} WHERE Name = ?', (institution,))
            existing_inst = cursor.fetchone()

            if existing_inst is None:
                cursor.execute(f"INSERT INTO Institutions_{y} (Name, Place) "
                        f"VALUES (?, ?)", (institution, country))
            cursor.execute(f'SELECT id_institution FROM Institutions_{y} WHERE Name = ?', (institution,))
            id_institution = cursor.fetchone()[0]
            cursor.execute(f"INSERT INTO Authors_Institutions_{y} (id_author, id_institution) "
                            f"VALUES (?, ?)", (id_author, id_institution))

    conn.commit()
    conn.close()


def insert_papers_authors(args):
    conference_name, title, authors, y = args

    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(f'../database/{conference_name}.db')
    cursor = conn.cursor()

    # insert the paper into the papers table
    cursor.execute(f"INSERT INTO Papers_{y} (Name) VALUES (?)", (title,))

    for a, inst in authors.items():
        cursor.execute(f'SELECT id_author FROM Authors_{y} WHERE Name = ?', (a,))
        id_author = cursor.fetchone()
        if id_author is not None: # set the author's paper_issuer to 1 if it exists in the table
            cursor.execute(f"UPDATE Authors_{y} SET paper_issuer = 1 WHERE id_author = ?", (id_author[0],))
        else:   # insert the author if it doesn't exist
            cursor.execute(f"INSERT INTO Authors_{y} (Name, member, paper_issuer) VALUES (?, 0, 1)",
                           (a, ))

        cursor.execute(f"SELECT id_author FROM Authors_{y} WHERE Name = ?", (a,))
        id_author = cursor.fetchone()[0]
        cursor.execute(f"SELECT id_paper FROM Papers_{y} WHERE Name = ?", (title,))
        id_paper = cursor.fetchone()[0]
        # add the relationship between the authors and the papers
        cursor.execute(f"INSERT INTO Authors_Papers_{y} (id_author, id_paper) VALUES (?, ?)", (id_author, id_paper))

        if inst is None:
            continue
        for institution, country in inst.items():
            cursor.execute(f'SELECT Name FROM Institutions_{y} WHERE Name = ?', (institution,))
            existing_inst = cursor.fetchone()
            if existing_inst is None:
                cursor.execute(f"INSERT INTO Institutions_{y} (Name, Place) "
                        f"VALUES (?, ?)", (institution, country))
            cursor.execute(f'SELECT id_institution FROM Institutions_{y} WHERE Name = ?', (institution,))
            id_institution = cursor.fetchone()[0]

            cursor.execute(f'SELECT COUNT(*) FROM Authors_Institutions_{y} WHERE id_author = ? AND id_institution = ?',
                           (id_author, id_institution))
            result = cursor.fetchone()[0]

            if result == 0:
                cursor.execute(f"INSERT INTO Authors_Institutions_{y} (id_author, id_institution) "
                                f"VALUES (?, ?)", (id_author, id_institution))

    # Commit the changes and close the connection after processing all papers
    conn.commit()
    conn.close()




if __name__ == '__main__':
    for conf in global_data.conferences:
        papers_data , committee_data = read_json_file(conf)

        for year in range(global_data.FIRST_YEAR, global_data.LAST_YEAR+1):
            create_tables(year, conf)

            if str(year) not in committee_data:
                continue
            dc = committee_data[str(year)]
            with Pool() as pool:
                for person, institution in dc.items():
                    pool.map(insert_names_members, [(conf, person, institution, year)])

        with Pool() as pool:
            for paper in papers_data:
                pool.map(insert_papers_authors, [(conf, paper['Title'], paper['Authors and Institutions'], paper['Year'])])