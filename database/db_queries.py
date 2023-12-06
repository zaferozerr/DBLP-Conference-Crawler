import sqlite3


def count_members_with_papers(conference_name, first_year, last_year):
    conn = sqlite3.connect(f'../database/{conference_name}.db')
    cursor = conn.cursor()

    result = {}
    for year in range(first_year, last_year+1):
        cursor.execute(f"SELECT COUNT(*) FROM Authors_{year} WHERE member = 1")
        count_all_members = cursor.fetchone()[0]

        cursor.execute(f'''SELECT COUNT(DISTINCT A.id_author)
                        FROM Authors_{year} A
                        INNER JOIN "Authors_Papers_{year}" AP ON A.id_author = AP.id_author
                        WHERE A.member = 1''')
        count_members_in_papers = cursor.fetchone()[0]

        result[year] = {"Members with papers": count_members_in_papers, "All members": count_all_members}

    return result


def obtain_countries_from_conference(conference_name, first_year, last_year):
    conn = sqlite3.connect(f'../database/{conference_name}.db')
    cursor = conn.cursor()

    result = {}

    for year in range(first_year, last_year + 1):
        cursor.execute(f'''
            SELECT Place, COUNT(*) AS Repetitions
            FROM Institutions_{year}
            GROUP BY Place
            ''')

        data = {}
        results = cursor.fetchall()
        for elem in results:
            key, value = elem
            key = "None" if key is None else key
            data[key] = value

        result[year] = data

    conn.close()
    return result


def papers_by_countries(conference_name, first_year, last_year):
    conn = sqlite3.connect(f'../database/{conference_name}.db')
    cursor = conn.cursor()

    result = {}
    for year in range(first_year, last_year + 1):
        cursor.execute(f'''
                        SELECT Papers_{year}.Name AS Paper_Name, GROUP_CONCAT(Institutions_{year}.Place) AS Institution_Places
                        FROM Papers_{year}
                        JOIN Authors_Papers_{year} ON Papers_{year}.id_paper = Authors_Papers_{year}.id_paper
                        JOIN Authors_{year} ON Authors_Papers_{year}.id_author = Authors_{year}.id_author
                        LEFT JOIN Authors_Institutions_{year} ON Authors_{year}.id_author = Authors_Institutions_{year}.id_author
                        LEFT JOIN Institutions_{year} ON Authors_Institutions_{year}.id_institution = Institutions_{year}.id_institution
                        GROUP BY Papers_{year}.id_paper;
                        ''')


        results = cursor.fetchall()
        result[year] = results

    conn.close()
    return result