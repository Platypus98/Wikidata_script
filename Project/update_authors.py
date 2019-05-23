#Импорт библиотек и сторонних файлов
import sqlite3
from wiki_data import execute_query
import time
import datetime
import logging
import json

#Настройка логирования
root_logger= logging.getLogger()
root_logger.setLevel(logging.INFO)
handler = logging.FileHandler('authors.log', 'w', 'utf-8')
root_logger.addHandler(handler)

#Настройка соединения с БД
db_path = 'book.db'
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

#SPARQL запрос к wikidata
query_authors_info = ''' 
SELECT DISTINCT ?person ?personLabel ?dateBirth ?placeBirthLabel ?dateDeath ?placeDeathLabel ?genderLabel WHERE {{
  ?person wdt:P31 wd:Q5 .
  ?person wdt:P106 ?personOccupation .

  ?person rdfs:label ?personLabel .
  
  ?person wdt:P569 ?dateBirth .  
  ?person wdt:P19 ?placeBirth .

  ?person wdt:P21 ?gender .
  
  FILTER REGEX (STR(?personLabel), "{first_name}", "i") .
  FILTER REGEX (STR(?personLabel), "{last_name}", "i") .
  FILTER (?dateBirth = "{date_birth}"^^xsd:dateTime)
  OPTIONAL {{ ?person wdt:P570 ?dateDeath .
             ?person wdt:P20 ?placeDeath . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru,en". }}
}} LIMIT 10

'''


def update_authors_info():

    cursor.execute('''
                   select
                        id
                       ,shortname
                       ,date_of_birth
                  from Author
                  where date_of_birth not null 
                    and fan_count not null
                  order by fan_count desc
                  limit 1''')


    for row in cursor.fetchall():
        try:
          if (row[1] == None) or (row[2] == None):
            root_logger.error(f"Not all fields are filled. Next author ... \n")
            continue

          first_name = row[1].split(" ")[0]
          last_name = row[1].split(" ")[-1]

          root_logger.info(f"Author - {first_name} {last_name}, {row[2]}")

          #Делается две попытки для получения данных
          for attempt in range(2):
            try:
              query_result = execute_query(query=query_authors_info, simplify=True, first_name=first_name, last_name=last_name, date_birth=row[2])
            except:
              root_logger.error(f"Attempt {attempt} - error")
              continue
            else:
              root_logger.info("Data received")
              break
          else:
            root_logger.error(f"Attempts ended. Next author ... \n")
            continue
          
          root_logger.info(f"Getting info - {query_result}")
          
          len_of_result = len(query_result)

          #Получили только один результат, без места и даты смерти
          if len_of_result == 5:

            root_logger.info("One result found")

            url_author = query_result[0].get("person")

            qid_author = url_author[url_author.rindex("/") + 1:]
            date_birth = query_result[1].get("dateBirth")[:10]
            place_birth = query_result[3].get("placeBirthLabel")
            gender =  query_result[4].get("genderLabel")

            #Вставка данных в БД
            cursor.execute('''
                        update Author
                        set qid             = ?,
                            date_of_birth_wiki  = ?,
                            place_of_birth_wiki = ?,
                            gender = ?
                        where id = ? 
                        ''', (qid_author, date_birth, place_birth, gender, row[0]))
            connection.commit()
            root_logger.info("Data inserted in DB. Next author ... \n")
          
          #Получили результаты с полной информацией
          elif len_of_result >= 7:

            if (len_of_result) >= 8:
              root_logger.info("Two or more result found. Getting first ...")
            else:
              root_logger.info("One result found.")


            query_result = query_result[:7]
            url_author = query_result[0].get("person")

            qid_author = url_author[url_author.rindex("/") + 1:]
            date_birth = query_result[1].get("dateBirth")[:10]
            date_death = query_result[3].get("dateDeath")[:10]
            place_birth = query_result[4].get("placeBirthLabel")
            place_death = query_result[5].get("placeDeathLabel")
            gender =  query_result[6].get("genderLabel")

            #Вставка данных в БД
            cursor.execute('''
                        update Author
                        set qid                 = ?,
                            date_of_birth_wiki  = ?,
                            date_of_death_wiki  = ?,
                            place_of_birth_wiki = ?,
                            place_of_death_wiki = ?,
                            gender              = ?
                        where id = ?
                        ''', (qid_author, date_birth, date_death, place_birth, place_death, gender, row[0]))
            connection.commit()

            root_logger.info(f"Data inserted in DB. Next author ...\n")
          else:
            root_logger.info(f"Data is not valid. Next author ...\n")
            continue
        except:
          continue


update_authors_info()