import sqlite3
from wiki_data import execute_query

import time
import datetime

import logging
import json

root_logger= logging.getLogger()
root_logger.setLevel(logging.INFO)
handler = logging.FileHandler('authors-json.log', 'w', 'utf-8')
root_logger.addHandler(handler)


db_path = 'book.db'
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

query_authors_info = ''' 
SELECT DISTINCT ?genreLabel WHERE {{
  
  ?person wdt:P136 ?genre
         
  BIND(wd:{qid} AS ?person) .
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru,en". }}
}} LIMIT 10
'''


def get_authors_json():
    
        cursor.execute('''
                    select
                        id
                        ,qid
                    from Author
                    where date_of_birth not null
                    order by fan_count desc
                    ''')

        for row in cursor.fetchall():
            
            with open("authors_genres.json", "a", encoding="utf-8") as f:
                author_data = {}

                if (row[1] == None):
                    root_logger.error(f"Not all fields are filled. Next author ... \n")
                    continue

                query_result = execute_query(query=query_authors_info, simplify=True, qid=row[1])

                root_logger.info(f"Id = {row[0]}, qid - {row[1]}")
                if len(query_result) > 0:

                    author_data['id'] = row[0]
                    author_data['qid'] = row[1]
                    genres = []

                    for i in query_result:
                        genres.append(i.get("genreLabel"))
                    
                    author_data['genres'] = genres
                    
                    json.dump(author_data, f, ensure_ascii=False)
                    f.write('\n')

                    root_logger.info("Data inserted in json. Next author ... \n")
                else:

                    root_logger.info(f"Data is not valid. Next author ...\n")
                    continue


get_authors_json()