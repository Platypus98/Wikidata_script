# База знаний по книгам

Зона ответственности: Денис Панин, Илья Голышков ( dpanin , Platypus98 )

## Установка

Выполнить в консоли:

```
git clone https://github.com/Platypus98/Wikidata_script.git
cd Wikidata_script/Project
```

## Запуск поиска информации по авторам

1. В консоли необходимо выполнить:

`python update_authors.py`


## Запуск поиска информации по книгам

1. В консоли необходимо выполнить:

`python update_books_by_search.py`

## Запуск получения информации по жанрам, в которых писал автор:

1. После того, как выполнился скрипт "update_authors.py", в консоли необходимо выполнить:

`python get_authors_genres.py`
