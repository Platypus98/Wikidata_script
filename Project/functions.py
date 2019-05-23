# functions.py
import requests

import pymorphy2
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
from server_queries import queries
import logging
import itertools


module_logger = logging.getLogger("App.functions")


def search_in_wikidata(query):
    '''
        Осуществляет поиск по Wikidata (страница https://www.wikidata.org/w/index.php?search)
        Возвращает словарь сущностей: ключ - Q-идентификатор сущности, значение -
            label - название сущности
            _isinstance - список того, чем является сущность
            occupation - список профессий
    '''
    API_ENDPOINT = "https://www.wikidata.org/w/api.php"
    module_logger.info(f"`search_in_wikidata`: query = {query}")
    # https://www.wikidata.org/w/api.php?action=help&modules=query%2Bsearch
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'srlimit': 500,
        'srsearch': query
    }

    r = requests.get(API_ENDPOINT, params=params)
    query = r.json()['query']
    if query['searchinfo']['totalhits'] == 0:
        return {}
    else:
        search_ids = [entity['title'] for entity in query['search']]

        # https://www.wikidata.org/w/api.php?action=help&modules=wbgetentities
        params = {
            'action': 'wbgetentities',
            'format': 'json',
            'languages': 'ru',
            'ids': '|'.join(search_ids[:50])  # ограничение к запросу - не более 50
        }
        r = requests.get(API_ENDPOINT, params=params)
        entities = r.json()['entities']

        found_entities = {}
        for qid in entities.keys():
            _isinstance, occupation = [], []
            if 'ru' in entities[qid]['labels']:
                label = entities[qid]['labels']['ru']['value']
            else:
                label = ''

            if 'P31' in entities[qid]['claims']:  # P:is instance
                for val in entities[qid]['claims']['P31']:
                    _isinstance.append(val['mainsnak']['datavalue']['value']['id'])
                found_entities[qid] = {'label': label, '_isinstance': _isinstance}
            else:
                found_entities[qid] = {'label': label, '_isinstance': []}

            if 'P106' in entities[qid]['claims']:  # P:occupation
                for val in entities[qid]['claims']['P106']:
                    occupation.append(val['mainsnak']['datavalue']['value']['id'])
                found_entities[qid]['occupation'] = occupation
            else:
                found_entities[qid]['occupation'] = []
        return found_entities


def filter_entities(entities, classes):
    '''
        Фильтрует список сущностей: оставляет только те сущности, для которых
        выполняются условия classes
        Пример: filter_entities(x, classes={'_isinstance': 'Q5', 'occupation':'Q36180'})
        оставит людей (Q5) с профессией писатель (Q36180)
    '''
    filtered = {}
    for qid, entity in entities.items():
        is_good = True
        for prop, value in classes.items():
            if value not in entity[prop]:
                is_good = False
                break
        if is_good:
            count_out = execute_query(queries['help_count_out_props']['query'], qid=qid)[0]['countOut']
            count_in = execute_query(queries['help_count_in_props']['query'], qid=qid)[0]['countIn']
            entity['total_props'] = int(count_out) + int(count_in)
            filtered[qid] = entity
    return filtered


# filter_writers = lambda x: filter_entities(x, classes={'_isinstance': 'Q5'}) #, 'occupation':'Q36180'
# filter_books = lambda x: filter_entities(x, classes={'_isinstance': 'Q7725634'})            

def filter_books(entities):
    '''
        Фильтрует список сущностей: остаются те, кто является литературным произведением (Q7725634) ИЛИ является книгой (Q571)
    '''
    filtered = {}
    for qid, entity in entities.items():
        if 'Q7725634' in entity['_isinstance'] or 'Q571' in entity['_isinstance'] or 'Q47461344' in entity['_isinstance']:
            count_out = execute_query(queries['help_count_out_props']['query'], qid=qid)[0]['countOut']
            count_in = execute_query(queries['help_count_in_props']['query'], qid=qid)[0]['countIn']
            entity['total_props'] = int(count_out) + int(count_in)
            filtered[qid] = entity
    return filtered


def filter_writers(entities):
    '''
        Фильтрует список сущностей: остаются те, кто
            1) является человеком (Q5) И
            2) являются по профессии писателем ИЛИ на них ссылается хоть одна книга
    '''
    filtered = {}
    for qid, entity in entities.items():
        if 'Q5' not in entity['_isinstance']:  # не человек
            continue
        else:
            count_books = int(execute_query(queries['help_count_books']['query'], author_id=qid)[0]['cBooks'])
            if 'Q36180' in entity['occupation'] or count_books > 0:  # проф: писатель или есть связанные книги
                count_out = execute_query(queries['help_count_out_props']['query'], qid=qid)[0]['countOut']
                count_in = execute_query(queries['help_count_in_props']['query'], qid=qid)[0]['countIn']
                entity['total_props'] = int(count_out) + int(count_in)
                filtered[qid] = entity
    return filtered


filters = {
    'book': filter_books,
    'author': filter_writers
}


def get_qid(query, param_type=None):
    '''
        Находит Q-идентификатор сущности query в Wikidata
        param_type - тип сущности (author для авторов и book для произведений)
        Если поиск находит несколько сущностей, то возвращает код сущности, имеющей наибольшее количество связей
    '''
    try:
        # if param_type == 'author': #возможно не потребуется, если получится получить норм. форму произведения
        # 	query = author_name_to_normal(query)
        # elif param_type == 'book':
        # 	query = book_name_to_normal(query)
        # else:
        # 	query = [query]
        query = [query]
        print(f"`get_qid`: query = {query}")
        module_logger.info(f"`get_qid`: query = {query}")
        for possible_query in query:
            search = search_in_wikidata(possible_query)
            if param_type is not None:
                filter_func = filters[param_type]
                filtered = filter_func(search)
            else:
                filtered = search
            if len(filtered):
                # qids = list(filtered.keys())
                qids = sorted(filtered, key=lambda x: filtered[x]['total_props'], reverse=True)
                print(f"`get_qid`: {filtered}")
                print(f"`get_qid`: возвращает qid={qids[0]}, entity={search[qids[0]]}")
                module_logger.info(f"`get_qid`: возвращает qid={qids[0]}, entity={search[qids[0]]}")
                return qids[0]
        else:
            return {}

    except Exception as e:
        module_logger.error(f"`get_qid`: Произошла ошибка: {e}")
        return None


def get_qid_with_label(query, param_type=None):
    '''
        Находит Q-идентификатор сущности query в Wikidata
        param_type - тип сущности (author для авторов и book для произведений)
        Если поиск находит несколько сущностей, то возвращает код сущности, имеющей наибольшее количество связей
    '''
    try:
        # if param_type == 'author': #возможно не потребуется, если получится получить норм. форму произведения
        # 	query = author_name_to_normal(query)
        # elif param_type == 'book':
        # 	query = book_name_to_normal(query)
        # else:
        # 	query = [query]
        query = [query]
        print(f"`get_qid`: query = {query}")
        module_logger.info(f"`get_qid`: query = {query}")
        for possible_query in query:
            search = search_in_wikidata(possible_query)
            if param_type is not None:
                filter_func = filters[param_type]
                filtered = filter_func(search)
            else:
                filtered = search
            if len(filtered):
                # qids = list(filtered.keys())
                qids = sorted(filtered, key=lambda x: filtered[x]['total_props'], reverse=True)
                print(f"`get_qid`: {filtered}")
                print(f"`get_qid`: возвращает qid={qids[0]}, entity={search[qids[0]]['label']}")
                module_logger.info(f"`get_qid`: возвращает qid={qids[0]}, entity={search[qids[0]]['label']}")
                return qids[0], search[qids[0]]['label']
        else:
            return {}

    except Exception as e:
        module_logger.error(f"`get_qid`: Произошла ошибка: {e}")
        return None


def find_template(question):
    '''
        Находит подходящий к вопросу question шаблон, возвращает его и список выделенных параметров
    '''
    for template in templates:
        found_parts = sum([1 for part in template['parts'] if part in question])
        if found_parts == len(template['parts']):
            params = {}
            for i in range(len(template['parts']) - 1):
                b = template['parts'][i]
                e = template['parts'][i + 1]
                name = template['params'][i]
                bind = question.index(b) + len(b)
                eind = question.index(e)
                params[name] = question[bind:eind]
            return template, params
    return None, None


def get_matches(text, extractor):
    '''
        Возвращает список размеченных именованных сущностей с правилами extractor
    '''
    if isinstance(extractor, Extractor):
        matches = extractor(text)
        facts = [_.fact.as_json for _ in matches]
        return facts
    elif isinstance(extractor, list):
        res = []
        for ex in extractor:
            matches = ex(text)
            facts = [_.fact.as_json for _ in matches]
            res += matches
            print(f'Finished with {ex}')
        return res


def get_name(facts):
    '''
        Соединяет части facts в одну строку через пробел и возвращает список
    '''
    if len(facts):
        return [' '.join(fact.values()) for fact in facts]
    else:
        return None


def author_name_to_normal(name):
    '''
        Переводит имя автора name в нормальную форму с помощью Natasha
        Важно: name не должно содержать предлогов
    '''
    normalized = get_name(get_matches(name, SimpleNamesExtractor()))
    if normalized:
        return normalized
    else:
        return name


def book_name_to_normal(name):
    '''
        Переводит название произведения name в нормальную форму. Для этого
        каждое слово в названии переводится в нормальную форму и
        возращается список их всевозможных комбинаций
        Важно: name не должно содержать предлогов
    '''
    morph = pymorphy2.MorphAnalyzer()
    words_forms = []
    for word in name.split():
        normal_forms = list(set([parsed.normal_form for parsed in morph.parse(word)]))
        words_forms.append(normal_forms)
    return [' '.join(comb) for comb in list(itertools.product(*words_forms))]


def author_name_from_question(question):
    matches = NamesExtractor()(question)
    names = []
    for match in matches:
        start, stop = match.span
        names.append({
            'start': start,
            'stop': stop,
            'name': question[start:stop],
            'normal_form': ' '.join(match.fact.as_json.values())
        })
    return names


def book_name_from_question(question, loadedTitleExtractor = None):
	extractor = title.titleExtractor() if loadedTitleExtractor is None else loadedTitleExtractor
	spans = extractor.get_spans(question)
	normal_forms = extractor.find_titles(question)
	books = []
	for span, normal_form in zip(spans, normal_forms):
		start, stop = span
		books.append({
			'start' : start,
			'stop' : stop,
			'name' : question[start:stop],
			'normal_form': normal_form
		})
	return books


def execute_query(query, simplify = True, **params):
	'''
		Выполняет SPARQL-запрос query с параметрами params 
		Если simplify = True, то из результатом удаляется служебная информация
		Возращает результат выполнения запроса
	'''
	sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
	sparql.setQuery(query.format(**params))
	# print('query=', query.format(**params))
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	if simplify:
		simplified = []
		for res in results['results']['bindings']:
			simplified.append({k: v['value'] for k, v in res.items()})
		return simplified 
	else:
		return results['results']['bindings']