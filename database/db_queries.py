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

def obtain_institutions_conference(conference_name, first_year, last_year):
    conn = sqlite3.connect(f'../database/{conference_name}.db')
    cursor = conn.cursor()

    result = {}
    for year in range(first_year, last_year + 1):
        cursor.execute(f'SELECT Name, Place FROM Institutions_{year};')
        results = cursor.fetchall()
        result[year] = results

    conn.close()
    return result


def obtain_num_papers_only_us(conference_name, first_year, last_year):
    conn = sqlite3.connect(f'../database/{conference_name}.db')
    cursor = conn.cursor()

    result = {}
    for year in range(first_year, last_year + 1):
        cursor.execute(f'''SELECT COUNT(DISTINCT p.id_paper) AS num_papers_us
                        FROM Papers_{year} p
                        JOIN Authors_Papers_{year} ap ON p.id_paper = ap.id_paper
                        WHERE NOT EXISTS (
                            SELECT 1
                            FROM Authors_Papers_{year} ap_other
                            JOIN Authors_Institutions_{year} ai_other ON ap_other.id_author = ai_other.id_author
                            JOIN Institutions_{year} i_other ON ai_other.id_institution = i_other.id_institution
                            WHERE ap_other.id_paper = p.id_paper
                              AND i_other.Place <> 'US');
                        ''')
        results = cursor.fetchall()[0]
        result[year] = results[0]

    conn.close()
    return result


def obtain_num_papers(conference_name, first_year, last_year):
    conn = sqlite3.connect(f'../database/{conference_name}.db')
    cursor = conn.cursor()

    result = {}
    for year in range(first_year, last_year + 1):
        cursor.execute(f'''SELECT COUNT(*) AS Num_Papers
                        FROM Papers_{year};
                        ''')

        results = cursor.fetchall()[0]
        result[year] = results[0]

    conn.close()
    return result


def top_institutions(conference_name, first_year, last_year):
    conn = sqlite3.connect(f'../database/{conference_name}.db')
    cursor = conn.cursor()

    result = {}
    for year in range(first_year, last_year + 1):
        cursor.execute(f'''SELECT Institutions_{year}.Name AS InstitutionName, Institutions_{year}.Place AS Country, COUNT(DISTINCT Papers_{year}.id_paper) AS PaperCount
                        FROM Institutions_{year}
                        JOIN Authors_Institutions_{year} ON Institutions_{year}.id_institution = Authors_Institutions_{year}.id_institution
                        JOIN Authors_Papers_{year} ON Authors_Institutions_{year}.id_author = Authors_Papers_{year}.id_author
                        JOIN Papers_{year} ON Authors_Papers_{year}.id_paper = Papers_{year}.id_paper
                        GROUP BY Institutions_{year}.id_institution
                        ORDER BY PaperCount DESC
                        LIMIT 10;
                        ''')

        results = cursor.fetchall()
        result[year] = results
        """
        for res in results:
            print(f'Year: {year} -> Institution: {res[0]}, {res[1]} // Total Counts: {res[2]}')
        """

    conn.close()
    return result
