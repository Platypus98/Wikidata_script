from functions import execute_query, filter_books, search_in_wikidata
import sqlite3
import logging
from nltk.metrics import *

#Настройка логирования
root_logger= logging.getLogger()
root_logger.setLevel(logging.INFO)
handler = logging.FileHandler('books_search.log', 'w', 'utf-8')
root_logger.addHandler(handler)


db_path = 'book.db'
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

def update_books_by_search():
    cursor.execute('''
                   select
                        b.id
                       ,b.name
                  from Book as b
                  order by b.read_count DESC
                  limit 1
                  ''')

    
    for row in cursor.fetchall():
        try:
            name = row[1]
            name = name.replace('"', '')
            #name = name.replace("»", '')
            #name = name.replace("«", '')
            name = name.replace("'", '')
            results = filter_books(search_in_wikidata(row[1]))
            
            root_logger.info(f"Find: {results}, len: {len(results)}")

            if len(results) == 1:
                for k in results.keys():
                    qid_book = k

                cursor.execute('''
                            update Book
                            set qid = ?
                            where id = ?
                            ''', (qid_book, row[0]))

                root_logger.info(f"Book inserted in DB. \n")
                connection.commit()

            elif len(results) >=2:

                min_distance = 0
                qid_book_result = ""
                for k in results.keys():
                    qid = k
                    cur_book_label = results.get(k).get('label') 
                    min_distance = edit_distance(name, cur_book_label)

                for k in results.keys():
                    qid = k
                    cur_book_label = results.get(k).get('label')
                    distance = edit_distance(name, cur_book_label)

                    if distance < min_distance:
                        min_distance = distance
                        qid_book_result = k
                
                if qid_book_result == "":
                    qid_book_result = list(results.keys())[0]
                
                root_logger.info(f"Select: {qid_book_result}")

                cursor.execute('''
                            update Book
                            set qid = ?
                            where id = ?
                            ''', (qid_book_result, row[0]))

                root_logger.info(f"Book inserted in DB. \n")
                connection.commit()
        except:
            continue
                

update_books_by_search()