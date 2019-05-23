from SPARQLWrapper import SPARQLWrapper, JSON

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
			for k, v in res.items():
				simplified.append({
					k: v['value']
				})
		return simplified 
	else:
		return results['results']['bindings']	